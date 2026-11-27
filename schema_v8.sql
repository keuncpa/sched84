-- 84부 일정표 v8: 기존 엑셀 일정 옮기기 지원
--  1) events.source   : 어디서 온 일정인지 (앱에서 직접 넣은 일정은 null, 엑셀에서 옮긴 일정은 'excel-…')
--  2) profiles.pending: 아직 가입하지 않은 팀원의 "이름만 먼저 등록한 자리" (true). 가입하면 관리자가 연결
--  3) link_member()   : 이름만 등록해 둔 자리의 일정을 실제 가입 계정으로 넘기고 그 자리를 없앰 (관리자만)

alter table public.events   add column if not exists source text check (source is null or char_length(source) <= 30);
alter table public.profiles add column if not exists pending boolean not null default false;

create or replace function public.protect_profile_flags() returns trigger
language plpgsql security definer set search_path = '' as $$
begin
  if (select auth.uid()) is not null and not public.is_admin() then
    new.approved := old.approved;
    new.is_admin := old.is_admin;
    new.sort     := old.sort;
    new.left_at  := old.left_at;
    new.pending  := old.pending;
  end if;
  new.id := old.id;
  new.created_at := old.created_at;
  return new;
end;
$$;

create or replace function public.link_member(p_from uuid, p_to uuid) returns void
language plpgsql security definer set search_path = '' as $$
declare v_sort integer;
begin
  if not public.is_admin() then raise exception 'permission denied'; end if;
  if p_from = p_to then raise exception 'same profile'; end if;
  select sort into v_sort from public.profiles where id = p_from and pending;
  if not found then raise exception 'not a pending profile'; end if;
  if not exists (select 1 from public.profiles where id = p_to and not pending) then raise exception 'target not found'; end if;
  -- 두 쪽 모두 같은 일정에 들어 있으면 한쪽만 남김
  delete from public.event_members a using public.event_members b
   where a.user_id = p_from and b.user_id = p_to and a.event_id = b.event_id;
  update public.event_members set user_id = p_to where user_id = p_from;
  update public.events set owner_id = p_to where owner_id = p_from;
  update public.profiles set approved = true, left_at = null, sort = v_sort where id = p_to;
  delete from public.profiles where id = p_from;
end;
$$;
revoke all on function public.link_member(uuid, uuid) from public, anon;
grant execute on function public.link_member(uuid, uuid) to authenticated;
