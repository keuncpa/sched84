// 서버(Supabase) 연결 설정 — 두 값을 채우면 실제 공유 모드로 동작합니다.
// 비워 두면 "데모 모드"(이 기기에만 저장)로 열립니다.
// 주의: 여기에는 Publishable key(sb_publishable_...)만 넣습니다. Secret key(sb_secret_...)는 절대 넣지 마세요.
window.APP_CONFIG = {
  SUPABASE_URL: "https://hfctslnxpawmolkcndgz.supabase.co",   // 예: "https://abcdefghijkl.supabase.co"
  SUPABASE_KEY: "sb_publishable_7hmSXKNz4k804uV7m4aglw_xA7oxx1A",   // 예: "sb_publishable_..."
  DEPT_NAME: "84부",
  // 배정 알림용 공개 키 (공개되어도 되는 값). 비공개 키는 Supabase Edge Functions > Secrets 에만 넣습니다.
  VAPID_PUBLIC_KEY: "BEegkz_xfp0N5M3S1_d5oCAU0_m-GvIURsvulx4-27f3EAxWAv-cvSFb6OEp6_VwpBoahwnp5BZvVqT92WDD5ns",
};
