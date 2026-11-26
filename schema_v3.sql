-- 84부 일정표 v3 — 일정 유형(카테고리)을 관리자가 직접 관리
-- schema.sql, schema_v2.sql 을 실행한 프로젝트에 "추가로" 한 번 실행합니다.
-- 규칙 요약
--   · 유형 목록은 승인된 부서원 모두 조회, 추가·수정·삭제는 관리자만
--   · 이미 일정에서 쓰고 있는 유형은 삭제할 수 없음(대신 "숨김" 처리) → 기존 일정이 깨지지 않음

create table public.categories (
  id         text primary key default ('c' || replace(gen_random_uuid()::text, '-', '')),
  label      text not null check (char_length(label) between 1 and 12),
  color      text not null default 'blue' check (color in ('blue','green','red','purple','orange','teal','pink','gray')),
  shared     boolean not null default false,   -- true: 팀 보기에서 "부서 공통" 줄에 표시 (특정인 일정이 아닌 부서 전체 일정)
  active     boolean not null default true,    -- false: 숨김 (새 일정에서 선택 불가, 기존 일정은 그대로 표시)
  sort       integer not null default 100,
  created_at timestamptz not null default now()
);

-- 기존 4개 유형을 그대로 옮김 (기존 일정의 type 값과 같은 id)
insert into public.categories (id, label, color, shared, sort) values
  ('field',    '필드·감사', 'blue',   false, 10),
  ('leave',    '휴가·교육', 'green',  false, 20),
  ('deadline', '마감·기한', 'red',    false, 30),
  ('dept',     '부서 행사', 'purple', true,  40);

-- 일정의 유형이 "고정 4개"가 아니라 "유형 목록에 있는 것"이면 되도록 변경
alter table public.events drop constraint events_type_check;
alter table public.events
  add constraint events_type_fkey foreign key (type) references public.categories(id)
  on update cascade on delete restrict;

alter table public.categories enable row level security;
revoke all on public.categories from anon;
grant select, insert, update, delete on public.categories to authenticated;

create policy "categories: 승인된 부서원이 조회"
  on public.categories for select to authenticated
  using (public.is_approved());

create policy "categories: 관리자만 추가"
  on public.categories for insert to authenticated
  with check (public.is_admin());

create policy "categories: 관리자만 수정"
  on public.categories for update to authenticated
  using (public.is_admin()) with check (public.is_admin());

create policy "categories: 관리자만 삭제"
  on public.categories for delete to authenticated
  using (public.is_admin());
