-- 84부 일정표 v10: 일정 휴지통 (삭제한 일정을 30일 동안 보관, 관리자가 복구)
--  events.deleted_at 에 값이 있으면 "휴지통에 있는 일정". 앱의 일정 조회는 deleted_at 이 비어 있는 것만 가져옴.
--  30일이 지난 것은 다음에 누군가 일정을 지우거나 관리자가 휴지통을 열 때 완전히 지워짐.

alter table public.events add column if not exists deleted_at timestamptz;
create index if not exists events_deleted_idx on public.events (deleted_at) where deleted_at is not null;

-- 휴지통으로 보내기: 지금까지 "삭제"가 되던 사람과 같음 (본인 일정, 또는 관리자)
create or replace function public.trash_event(p_id uuid) returns void
language plpgsql security definer set search_path = '' as $$
begin
  if not public.is_approved() then raise exception 'permission denied'; end if;
  update public.events set deleted_at = now()
   where id = p_id and deleted_at is null and (owner_id = (select auth.uid()) or public.is_admin());
  if not found then raise exception 'permission denied'; end if;
  delete from public.events where deleted_at < now() - interval '30 days';
end;
$$;

-- 복구: 관리자만
create or replace function public.restore_event(p_id uuid) returns void
language plpgsql security definer set search_path = '' as $$
begin
  if not public.is_admin() then raise exception 'permission denied'; end if;
  update public.events set deleted_at = null where id = p_id and deleted_at is not null;
  if not found then raise exception 'not in trash'; end if;
end;
$$;

-- 30일 지난 것 비우기: 관리자가 휴지통을 열 때 호출
create or replace function public.purge_trash() returns void
language plpgsql security definer set search_path = '' as $$
begin
  if not public.is_admin() then raise exception 'permission denied'; end if;
  delete from public.events where deleted_at < now() - interval '30 days';
end;
$$;

revoke all on function public.trash_event(uuid), public.restore_event(uuid), public.purge_trash() from public, anon;
grant execute on function public.trash_event(uuid), public.restore_event(uuid), public.purge_trash() to authenticated;
