-- 84부 일정표 v7: 구성원 표시 순서(서열)
-- 관리자가 [설정 > 구성원 순서]에서 ▲▼로 정한 순서. 팀 보기·엑셀·배정 목록이 이 순서로 나옴.
-- 새로 가입한 사람은 큰 값(맨 아래)에서 시작.

alter table public.profiles add column if not exists sort integer not null default 100000;

-- 순서는 관리자만 바꿀 수 있음 (승인/관리자 값과 같은 방식으로 보호)
create or replace function public.protect_profile_flags() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  if (select auth.uid()) is not null and not public.is_admin() then
    new.approved := old.approved;
    new.is_admin := old.is_admin;
    new.sort     := old.sort;
  end if;
  new.id := old.id;
  new.created_at := old.created_at;
  return new;
end;
$$;
