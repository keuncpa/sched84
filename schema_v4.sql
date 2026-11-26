-- 84부 일정표 v4 — 퇴사 처리(일정 보존) + 거래처
-- schema.sql, schema_v2.sql, schema_v3.sql 을 실행한 프로젝트에 "추가로" 한 번 실행합니다.
-- 규칙 요약
--   · 퇴사 처리: 그 사람은 일정표를 볼 수 없게 되지만, 그 사람이 등록했거나 배정됐던 일정은 그대로 남음
--   · Supabase 대시보드에서 로그인 계정 자체를 지워도 일정과 이름 기록은 남음
--   · 거래처 목록은 승인된 부서원 모두 조회, 추가·수정·삭제는 관리자만
--   · 일정에 쓰인 거래처는 삭제할 수 없음(대신 "숨김")

-- 1) 퇴사 처리 --------------------------------------------------------------
alter table public.profiles add column left_at timestamptz;   -- 값이 있으면 퇴사자

-- 로그인 계정(auth.users)이 지워져도 프로필 기록은 남도록 연결을 끊음
-- (기존에는 계정 삭제 → 프로필 삭제 → 그 사람의 일정까지 연쇄 삭제되었음)
alter table public.profiles drop constraint profiles_id_fkey;

-- 대시보드에서 계정을 지우면 자동으로 퇴사 처리로 표시
create function public.handle_user_deleted() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  update public.profiles
     set approved = false, is_admin = false, left_at = coalesce(left_at, now())
   where id = old.id;
  return old;
end;
$$;
create trigger on_auth_user_deleted
  after delete on auth.users
  for each row execute function public.handle_user_deleted();

-- 본인이 스스로 퇴사/복귀 값을 바꾸지 못하게 (승인·관리자 값과 같은 보호)
create or replace function public.protect_profile_flags() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  if (select auth.uid()) is not null and not public.is_admin() then
    new.approved := old.approved;
    new.is_admin := old.is_admin;
    new.left_at  := old.left_at;
  end if;
  new.id := old.id;
  new.created_at := old.created_at;
  return new;
end;
$$;

-- 승인이 풀리면(퇴사·승인 취소) 그 사람 기기의 알림 등록을 지움
create function public.cleanup_on_unapprove() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  if old.approved and not new.approved then
    delete from public.push_subscriptions where user_id = new.id;
  end if;
  return new;
end;
$$;
create trigger profiles_cleanup
  after update on public.profiles
  for each row execute function public.cleanup_on_unapprove();

-- 2) 거래처 -----------------------------------------------------------------
create table public.clients (
  id         uuid primary key default gen_random_uuid(),
  name       text not null check (char_length(name) between 1 and 30),
  color      text not null default 'blue' check (color in ('blue','green','red','purple','orange','teal','pink','gray')),
  active     boolean not null default true,    -- false: 숨김 (새 일정에서 선택 불가, 기존 일정은 그대로 표시)
  created_at timestamptz not null default now()
);
create unique index clients_name_key on public.clients (lower(name));

alter table public.events add column client_id uuid references public.clients(id) on delete restrict;
create index events_client_idx on public.events (client_id);

alter table public.clients enable row level security;
revoke all on public.clients from anon;
grant select, insert, update, delete on public.clients to authenticated;

create policy "clients: 승인된 부서원이 조회"
  on public.clients for select to authenticated
  using (public.is_approved());

create policy "clients: 관리자만 추가"
  on public.clients for insert to authenticated
  with check (public.is_admin());

create policy "clients: 관리자만 수정"
  on public.clients for update to authenticated
  using (public.is_admin()) with check (public.is_admin());

create policy "clients: 관리자만 삭제"
  on public.clients for delete to authenticated
  using (public.is_admin());
