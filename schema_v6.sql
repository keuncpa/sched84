-- 84부 일정표 v6 — 배정할 때 사람별 역할(매니저·인차지·시니어·스탭 등) 지정
-- schema_v5.sql 까지 실행한 프로젝트에 "추가로" 한 번 실행합니다.
-- 역할은 그 일정에서의 역할입니다(같은 사람이 일정마다 다른 역할일 수 있음). 비워 둘 수 있습니다.
alter table public.event_members add column role text check (role is null or char_length(role) between 1 and 10);

grant update on public.event_members to authenticated;
create policy "event_members: 관리자만 역할 수정"
  on public.event_members for update to authenticated
  using (public.is_admin()) with check (public.is_admin());
