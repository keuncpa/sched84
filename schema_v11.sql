-- 84부 일정표 v11: 한 일정 안에서 사람마다 다른 투입 기간
-- event_members.start_date / end_date 가 비어 있으면 그 사람은 일정의 전체 기간에 투입.
-- 값이 있으면 그 사람은 그 기간에만 투입(팀 보기·내 일정·엑셀의 그 사람 줄에 그 날짜에만 표시).
-- 일정 자체의 기간(events.start_date~end_date)은 가장 이른 날부터 가장 늦은 날까지.

alter table public.event_members add column if not exists start_date date;
alter table public.event_members add column if not exists end_date date;
alter table public.event_members drop constraint if exists event_members_period;
alter table public.event_members add constraint event_members_period check (start_date is null or end_date is null or end_date >= start_date);
