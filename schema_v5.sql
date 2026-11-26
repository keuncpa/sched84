-- 84부 일정표 v5 — 거래처 색상을 8가지에서 37가지로 확대
-- schema_v4.sql 까지 실행한 프로젝트에 "추가로" 한 번 실행합니다.
-- 색 값: 기존 8가지 이름, 또는 h<색상각>(연한 색) / s<색상각>(진한 색). 예: h200, s340
alter table public.clients drop constraint clients_color_check;
alter table public.clients add constraint clients_color_check
  check (color ~ '^(blue|green|red|purple|orange|teal|pink|gray|[hs][0-9]{1,3})$');
