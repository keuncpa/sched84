-- 84부 일정표 v9: 퇴사자를 목록에서 지우기
-- profiles.hidden = true 이면 [설정]의 퇴사자 목록에 더 이상 나오지 않음.
-- 줄 자체는 남겨 두므로 그 사람이 들어 있던 과거 일정과 이름 표시는 그대로 유지됨.

alter table public.profiles add column if not exists hidden boolean not null default false;

create or replace function public.protect_profile_flags() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  if (select auth.uid()) is not null and not public.is_admin() then
    new.approved := old.approved;
    new.is_admin := old.is_admin;
    new.sort     := old.sort;
    new.left_at  := old.left_at;
    new.pending  := old.pending;
    new.hidden   := old.hidden;
  end if;
  new.id := old.id;
  new.created_at := old.created_at;
  return new;
end;
$$;
