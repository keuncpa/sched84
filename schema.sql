-- 84부 일정표 — Supabase SQL Editor에 전체를 붙여넣고 한 번 실행합니다.
-- 규칙 요약
--   · 승인된 부서원만 일정을 볼 수 있음
--   · 일정 추가·수정·삭제는 본인 것만 (관리자는 정리 목적으로 삭제만 가능)
--   · 가장 먼저 가입한 사람이 자동으로 관리자 + 승인 상태가 됨
--   · 이후 가입자는 관리자가 앱 [설정]에서 승인해야 사용 가능

-- 1) 테이블 ---------------------------------------------------------------
create table public.profiles (
  id         uuid primary key references auth.users(id) on delete cascade,
  name       text not null check (char_length(name) between 1 and 30),
  title      text not null default '' check (char_length(title) <= 20),
  approved   boolean not null default false,
  is_admin   boolean not null default false,
  created_at timestamptz not null default now()
);

create table public.events (
  id         uuid primary key default gen_random_uuid(),
  owner_id   uuid not null references public.profiles(id) on delete cascade,
  type       text not null check (type in ('field','leave','deadline','dept')),
  title      text not null check (char_length(title) between 1 and 60),
  start_date date not null,
  end_date   date not null,
  memo       text not null default '' check (char_length(memo) <= 500),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint events_period check (end_date >= start_date)
);
create index events_period_idx on public.events (start_date, end_date);
create index events_owner_idx  on public.events (owner_id);

-- 2) 권한 판별 함수 ---------------------------------------------------------
create function public.is_approved() returns boolean
language sql stable security definer set search_path = '' as $$
  select exists (select 1 from public.profiles where id = (select auth.uid()) and approved);
$$;

create function public.is_admin() returns boolean
language sql stable security definer set search_path = '' as $$
  select exists (select 1 from public.profiles where id = (select auth.uid()) and approved and is_admin);
$$;

-- 3) 가입 시 프로필 자동 생성 (첫 가입자 = 관리자) -----------------------------
create function public.handle_new_user() returns trigger
language plpgsql security definer set search_path = '' as $$
declare
  is_first boolean;
begin
  select not exists (select 1 from public.profiles) into is_first;
  insert into public.profiles (id, name, approved, is_admin)
  values (
    new.id,
    coalesce(nullif(left(trim(new.raw_user_meta_data->>'name'), 30), ''), '이름없음'),
    is_first, is_first
  );
  return new;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- 4) 본인이 스스로 승인·관리자 값을 바꾸지 못하게 막기 ---------------------------
create function public.protect_profile_flags() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  -- 앱에서 들어온 요청(로그인 사용자)이고 관리자가 아니면 승인/관리자 값은 그대로 유지
  if (select auth.uid()) is not null and not public.is_admin() then
    new.approved := old.approved;
    new.is_admin := old.is_admin;
  end if;
  new.id := old.id;
  new.created_at := old.created_at;
  return new;
end;
$$;

create trigger profiles_protect
  before update on public.profiles
  for each row execute function public.protect_profile_flags();

create function public.touch_updated_at() returns trigger
language plpgsql set search_path = '' as $$
begin
  new.updated_at := now();
  new.owner_id := old.owner_id;   -- 일정의 주인은 바꿀 수 없음
  return new;
end;
$$;

create trigger events_touch
  before update on public.events
  for each row execute function public.touch_updated_at();

-- 5) 행 단위 보안(RLS) ------------------------------------------------------
alter table public.profiles enable row level security;
alter table public.events   enable row level security;

revoke all on public.profiles, public.events from anon;
grant select, update on public.profiles to authenticated;
grant select, insert, update, delete on public.events to authenticated;

create policy "profiles: 본인 또는 승인된 부서원이 조회"
  on public.profiles for select to authenticated
  using (id = (select auth.uid()) or public.is_approved());

create policy "profiles: 본인 수정, 관리자는 전체 수정"
  on public.profiles for update to authenticated
  using (id = (select auth.uid()) or public.is_admin())
  with check (id = (select auth.uid()) or public.is_admin());

create policy "events: 승인된 부서원만 조회"
  on public.events for select to authenticated
  using (public.is_approved());

create policy "events: 본인 일정만 추가"
  on public.events for insert to authenticated
  with check (owner_id = (select auth.uid()) and public.is_approved());

create policy "events: 본인 일정만 수정"
  on public.events for update to authenticated
  using (owner_id = (select auth.uid()) and public.is_approved())
  with check (owner_id = (select auth.uid()) and public.is_approved());

create policy "events: 본인 일정 삭제, 관리자는 정리용 삭제"
  on public.events for delete to authenticated
  using ((owner_id = (select auth.uid()) and public.is_approved()) or public.is_admin());
