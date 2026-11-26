-- 84부 일정표 v2 — 팀원 배정 + 배정 알림
-- 기존 schema.sql 을 이미 실행한 프로젝트에 "추가로" 한 번 실행합니다.
-- 규칙 요약
--   · 관리자만 일정에 팀원을 배정할 수 있음 (배정된 일정은 그 팀원들 일정표에 표시)
--   · 배정된 일정은 관리자라면 누구나 수정 가능 (관리자가 2명 이상일 때 서로 고칠 수 있게)
--   · 개인이 직접 넣은 일정은 종전대로 본인만 수정
--   · 알림 구독 정보(기기 주소)는 본인도 직접 조회할 수 없고, 등록/해제 함수로만 다룸

-- 1) 배정 테이블 ------------------------------------------------------------
create table public.event_members (
  event_id   uuid not null references public.events(id)   on delete cascade,
  user_id    uuid not null references public.profiles(id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (event_id, user_id)
);
create index event_members_user_idx on public.event_members (user_id);

alter table public.event_members enable row level security;
revoke all on public.event_members from anon;
grant select, insert, delete on public.event_members to authenticated;

create policy "event_members: 승인된 부서원이 조회"
  on public.event_members for select to authenticated
  using (public.is_approved());

create policy "event_members: 관리자만 배정"
  on public.event_members for insert to authenticated
  with check (
    public.is_admin()
    and exists (select 1 from public.profiles p where p.id = user_id and p.approved)
  );

create policy "event_members: 관리자만 배정 해제"
  on public.event_members for delete to authenticated
  using (public.is_admin());

-- 2) 배정된 일정은 관리자도 수정 가능하도록 수정 규칙 교체 -------------------------
drop policy "events: 본인 일정만 수정" on public.events;

create policy "events: 본인 일정 수정, 배정 일정은 관리자 수정"
  on public.events for update to authenticated
  using (
    (owner_id = (select auth.uid()) and public.is_approved())
    or (public.is_admin() and exists (select 1 from public.event_members m where m.event_id = id))
  )
  with check (
    (owner_id = (select auth.uid()) and public.is_approved())
    or (public.is_admin() and exists (select 1 from public.event_members m where m.event_id = id))
  );

-- 3) 알림 구독(기기) 테이블 — 직접 접근 불가, 아래 함수로만 사용 ---------------------
create table public.push_subscriptions (
  endpoint   text primary key check (char_length(endpoint) between 10 and 1000),
  user_id    uuid not null references public.profiles(id) on delete cascade,
  p256dh     text not null check (char_length(p256dh) between 20 and 200),
  auth       text not null check (char_length(auth) between 10 and 100),
  created_at timestamptz not null default now()
);
create index push_subscriptions_user_idx on public.push_subscriptions (user_id);

alter table public.push_subscriptions enable row level security;   -- 정책 없음 = 직접 조회·수정 불가
revoke all on public.push_subscriptions from anon, authenticated;

-- 이 기기에서 알림 받기 (같은 기기에 다른 사람이 로그인하면 주인이 바뀜)
create function public.register_push(p_endpoint text, p_p256dh text, p_auth text) returns void
language plpgsql security definer set search_path = '' as $$
begin
  if not public.is_approved() then
    raise exception 'not approved' using errcode = '42501';
  end if;
  if p_endpoint !~ '^https://' then
    raise exception 'invalid endpoint' using errcode = '22023';
  end if;
  insert into public.push_subscriptions (endpoint, user_id, p256dh, auth)
  values (p_endpoint, (select auth.uid()), p_p256dh, p_auth)
  on conflict (endpoint) do update
    set user_id = excluded.user_id, p256dh = excluded.p256dh, auth = excluded.auth, created_at = now();
end;
$$;

-- 이 기기 알림 끄기 (본인 것만)
create function public.unregister_push(p_endpoint text) returns void
language sql security definer set search_path = '' as $$
  delete from public.push_subscriptions
  where endpoint = p_endpoint and user_id = (select auth.uid());
$$;

-- 내 계정에 알림이 켜진 기기 수
create function public.my_push_count() returns integer
language sql stable security definer set search_path = '' as $$
  select count(*)::int from public.push_subscriptions where user_id = (select auth.uid());
$$;

-- 발송 대상 조회 (관리자 전용). 해당 일정에 실제로 배정된 사람의 기기만 돌려줌.
create function public.push_targets(p_event uuid, p_users uuid[]) returns jsonb
language plpgsql stable security definer set search_path = '' as $$
declare
  ev   jsonb;
  subs jsonb;
begin
  if not public.is_admin() then
    raise exception 'admin only' using errcode = '42501';
  end if;
  select jsonb_build_object('title', e.title, 'type', e.type, 'start_date', e.start_date, 'end_date', e.end_date)
    into ev from public.events e where e.id = p_event;
  if ev is null then
    return jsonb_build_object('event', null, 'subs', '[]'::jsonb);
  end if;
  select coalesce(jsonb_agg(jsonb_build_object('endpoint', s.endpoint, 'p256dh', s.p256dh, 'auth', s.auth)), '[]'::jsonb)
    into subs
  from public.push_subscriptions s
  join public.event_members m on m.user_id = s.user_id and m.event_id = p_event
  where s.user_id = any (p_users)
    and s.user_id <> (select auth.uid());       -- 배정한 본인에게는 보내지 않음
  return jsonb_build_object('event', ev, 'subs', subs);
end;
$$;

-- 더 이상 유효하지 않은 기기 주소 정리 (관리자 전용, 발송 함수가 호출)
create function public.push_prune(p_endpoints text[]) returns void
language plpgsql security definer set search_path = '' as $$
begin
  if not public.is_admin() then
    raise exception 'admin only' using errcode = '42501';
  end if;
  delete from public.push_subscriptions where endpoint = any (p_endpoints);
end;
$$;

revoke all on function public.register_push(text, text, text), public.unregister_push(text), public.my_push_count(),
  public.push_targets(uuid, uuid[]), public.push_prune(text[]) from public, anon;
grant execute on function public.register_push(text, text, text), public.unregister_push(text), public.my_push_count(),
  public.push_targets(uuid, uuid[]), public.push_prune(text[]) to authenticated;
