// 84부 일정표 — 배정 알림 발송 함수 (Supabase Edge Function 이름: notify)
//
// 동작: 관리자 앱이 { event_id, user_ids, kind } 를 보내면
//   1) 호출자의 로그인 토큰 그대로 DB 함수 push_targets 를 호출 (관리자가 아니면 DB가 거부)
//   2) 해당 일정에 실제로 배정된 사람들의 기기로 웹 푸시 전송
//   3) 더 이상 유효하지 않은 기기 주소는 정리
// 알림 문구는 DB에서 읽은 일정 정보로만 만듭니다 (호출자가 임의 문구를 보낼 수 없음).
//
// 필요한 비밀값(Edge Functions > Secrets): VAPID_PRIVATE_KEY
// 이 파일에는 비밀값이 없습니다. 아래 두 키는 공개용 키입니다.

const API_KEY = "sb_publishable_7hmSXKNz4k804uV7m4aglw_xA7oxx1A";
const VAPID_PUBLIC = "BEegkz_xfp0N5M3S1_d5oCAU0_m-GvIURsvulx4-27f3EAxWAv-cvSFb6OEp6_VwpBoahwnp5BZvVqT92WDD5ns";
const APP_URL = "https://keuncpa.github.io/sched84/";
const ALLOWED_ORIGIN = "https://keuncpa.github.io";

const cors = {
  "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { ...cors, "Content-Type": "application/json" } });

/* ---------- base64url ---------- */
const enc = new TextEncoder();
function b64uToBytes(s) {
  const b = atob(s.replace(/-/g, "+").replace(/_/g, "/").padEnd(Math.ceil(s.length / 4) * 4, "="));
  const out = new Uint8Array(b.length);
  for (let i = 0; i < b.length; i++) out[i] = b.charCodeAt(i);
  return out;
}
function bytesToB64u(bytes) {
  let s = "";
  for (const x of new Uint8Array(bytes)) s += String.fromCharCode(x);
  return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function concat(...parts) {
  const out = new Uint8Array(parts.reduce((n, p) => n + p.length, 0));
  let o = 0;
  for (const p of parts) { out.set(p, o); o += p.length; }
  return out;
}

/* ---------- VAPID (RFC 8292): 발신 서버 증명 ---------- */
let vapidKeyPromise = null;
function vapidKey() {
  if (!vapidKeyPromise) {
    const pub = b64uToBytes(VAPID_PUBLIC);
    const d = (Deno.env.get("VAPID_PRIVATE_KEY") || "").trim();
    vapidKeyPromise = crypto.subtle.importKey(
      "jwk",
      { kty: "EC", crv: "P-256", d, x: bytesToB64u(pub.slice(1, 33)), y: bytesToB64u(pub.slice(33, 65)), ext: true },
      { name: "ECDSA", namedCurve: "P-256" }, false, ["sign"],
    );
  }
  return vapidKeyPromise;
}
async function vapidHeader(endpoint) {
  const aud = new URL(endpoint).origin;
  const head = bytesToB64u(enc.encode(JSON.stringify({ typ: "JWT", alg: "ES256" })));
  const body = bytesToB64u(enc.encode(JSON.stringify({ aud, exp: Math.floor(Date.now() / 1000) + 12 * 3600, sub: APP_URL })));
  const sig = await crypto.subtle.sign({ name: "ECDSA", hash: "SHA-256" }, await vapidKey(), enc.encode(`${head}.${body}`));
  return `vapid t=${head}.${body}.${bytesToB64u(sig)}, k=${VAPID_PUBLIC}`;
}

/* ---------- 본문 암호화 (RFC 8291, aes128gcm) ---------- */
async function hkdf(salt, ikm, info, len) {
  const key = await crypto.subtle.importKey("raw", ikm, "HKDF", false, ["deriveBits"]);
  return new Uint8Array(await crypto.subtle.deriveBits({ name: "HKDF", hash: "SHA-256", salt, info }, key, len * 8));
}
async function encryptPayload(text, p256dh, auth) {
  const uaPublic = b64uToBytes(p256dh);
  const authSecret = b64uToBytes(auth);
  const uaKey = await crypto.subtle.importKey("raw", uaPublic, { name: "ECDH", namedCurve: "P-256" }, false, []);
  const local = await crypto.subtle.generateKey({ name: "ECDH", namedCurve: "P-256" }, true, ["deriveBits"]);
  const asPublic = new Uint8Array(await crypto.subtle.exportKey("raw", local.publicKey));
  const shared = new Uint8Array(await crypto.subtle.deriveBits({ name: "ECDH", public: uaKey }, local.privateKey, 256));

  const ikm = await hkdf(authSecret, shared, concat(enc.encode("WebPush: info\0"), uaPublic, asPublic), 32);
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const cek = await hkdf(salt, ikm, enc.encode("Content-Encoding: aes128gcm\0"), 16);
  const nonce = await hkdf(salt, ikm, enc.encode("Content-Encoding: nonce\0"), 12);

  const aes = await crypto.subtle.importKey("raw", cek, "AES-GCM", false, ["encrypt"]);
  const plain = concat(enc.encode(text), new Uint8Array([2]));          // 0x02 = 마지막 레코드 표시
  const cipher = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-GCM", iv: nonce }, aes, plain));

  const header = new Uint8Array(16 + 4 + 1 + asPublic.length);
  header.set(salt, 0);
  new DataView(header.buffer).setUint32(16, 4096);                       // 레코드 크기
  header[20] = asPublic.length;
  header.set(asPublic, 21);
  return concat(header, cipher);
}

async function sendPush(sub, payloadText) {
  const body = await encryptPayload(payloadText, sub.p256dh, sub.auth);
  const res = await fetch(sub.endpoint, {
    method: "POST",
    headers: {
      Authorization: await vapidHeader(sub.endpoint),
      "Content-Encoding": "aes128gcm",
      "Content-Type": "application/octet-stream",
      TTL: "86400",
      Urgency: "high",
    },
    body,
  });
  return res.status;
}

/* ---------- 알림 문구 ---------- */
const DOW = ["일", "월", "화", "수", "목", "금", "토"];
function md(s) {
  const [y, m, d] = s.split("-").map(Number);
  return `${m}.${d}(${DOW[new Date(Date.UTC(y, m - 1, d)).getUTCDay()]})`;
}
function message(ev, kind, id) {
  const period = ev.start_date === ev.end_date ? md(ev.start_date) : `${md(ev.start_date)} – ${md(ev.end_date)}`;
  return {
    title: kind === "update" ? "배정 일정이 변경되었습니다" : "새 일정이 배정되었습니다",
    body: `${ev.title} · ${period}`,
    url: APP_URL,
    tag: "ev-" + id,           // 같은 일정의 알림끼리만 서로 덮어씀
  };
}

async function rpc(name, args, authorization) {
  return fetch(`${Deno.env.get("SUPABASE_URL")}/rest/v1/rpc/${name}`, {
    method: "POST",
    headers: { apikey: API_KEY, Authorization: authorization, "Content-Type": "application/json" },
    body: JSON.stringify(args),
  });
}

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

async function handler(req) {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "POST") return json({ error: "method" }, 405);
  const authorization = req.headers.get("Authorization");
  if (!authorization) return json({ error: "login required" }, 401);
  if (!(Deno.env.get("VAPID_PRIVATE_KEY") || "").trim()) return json({ error: "VAPID_PRIVATE_KEY not set" }, 503);

  let input;
  try { input = await req.json(); } catch (_e) { return json({ error: "bad json" }, 400); }
  const users = Array.isArray(input.user_ids) ? input.user_ids.filter((u) => UUID.test(u)).slice(0, 100) : [];
  const kind = input.kind === "update" ? "update" : "assign";
  if (!UUID.test(input.event_id || "") || !users.length) return json({ error: "bad request" }, 400);

  const t = await rpc("push_targets", { p_event: input.event_id, p_users: users }, authorization);
  if (!t.ok) return json({ error: "not allowed" }, t.status === 401 ? 401 : 403);
  const { event, subs } = await t.json();
  if (!event || !subs.length) return json({ sent: 0, failed: 0, devices: 0 });

  const payload = JSON.stringify(message(event, kind, input.event_id));
  const results = await Promise.all(subs.map((s) => sendPush(s, payload).catch(() => 0)));
  const gone = subs.filter((_s, i) => results[i] === 404 || results[i] === 410).map((s) => s.endpoint);
  if (gone.length) await rpc("push_prune", { p_endpoints: gone }, authorization).catch(() => {});
  const sent = results.filter((c) => c >= 200 && c < 300).length;
  return json({ sent, failed: results.length - sent, devices: subs.length });
}

Deno.serve(handler);
