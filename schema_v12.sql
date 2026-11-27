-- 84부 일정표 v12: 거래처가 있는 일정은 제목(업무)을 비워 둘 수 있음
-- 거래처는 따로 표시(태그)하고 제목에는 업무만 적는 방식. 거래처가 없는 일정은 지금처럼 제목이 꼭 있어야 함.

alter table public.events drop constraint if exists events_title_check;
alter table public.events add constraint events_title_check check (char_length(title) <= 60 and (char_length(title) >= 1 or client_id is not null));

-- 배정 알림 문구: 제목 앞에 거래처 이름을 붙여서 보냄 (제목이 비어 있으면 거래처 이름만)
create or replace function public.push_targets(p_event uuid, p_users uuid[]) returns jsonb
language plpgsql stable security definer set search_path = '' as $$
declare
  ev   jsonb;
  subs jsonb;
begin
  if not public.is_admin() then
    raise exception 'admin only' using errcode = '42501';
  end if;
  select jsonb_build_object('title', btrim(coalesce((select c.name from public.clients c where c.id = e.client_id) || ' ', '') || e.title),
                            'type', e.type, 'start_date', e.start_date, 'end_date', e.end_date)
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
