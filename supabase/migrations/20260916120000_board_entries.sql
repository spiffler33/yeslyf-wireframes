-- yeslyf product board: append-only write-back (phase 11, Vatsal, 16 Sep 2026).
-- One table. Every comment, verdict and field edit on every page is one row; the latest row per
-- (page, item_id, field) is the current value; rows are never updated or deleted.
-- Run once in the Supabase dashboard: SQL Editor, New query, paste this file, Run.
--
-- page     board (Meeting, Gaps and Inputs tabs share it) | wireframes_v02 | integrations | admin_v02 | changelog | events
-- item_id  a screen id (A01), an integration or owed row (I01, W01), or item:T1 | qa:12 | gap:G03 on the board pages
-- field    what was edited: verdict, reason, text, choice, decided, note, accept, status, owner, date, sandbox_date, ...
-- value    the new value as text; empty means cleared
-- who      the identity picked in the page (a first name, Spinach or Compliance); may be empty
-- kind     comment (free text) | verdict (a choice among fixed options) | field_edit (everything else)

create table public.board_entries (
  id         bigint generated always as identity primary key,
  page       text not null,
  item_id    text not null,
  field      text not null,
  value      text not null default '',
  who        text not null default '',
  kind       text not null check (kind in ('comment', 'verdict', 'field_edit')),
  created_at timestamptz not null default now()
);

create index board_entries_page_item_idx on public.board_entries (page, item_id, id);

comment on table public.board_entries is
  'yeslyf product board write-back: append-only; the latest row per page, item_id and field is the current value';

alter table public.board_entries enable row level security;

-- The client roles may add rows and read them, nothing else. No update or delete policy exists, and the
-- update, delete and truncate privileges are revoked too, so an update or delete with the anon key is
-- refused with "permission denied" (42501) instead of matching zero rows silently.
-- The insert grant names the columns, so a client cannot set id or created_at.
revoke all on table public.board_entries from anon, authenticated;
grant select on table public.board_entries to anon, authenticated;
grant insert (page, item_id, field, value, who, kind) on table public.board_entries to anon, authenticated;

create policy "anon insert" on public.board_entries
  for insert to anon, authenticated with check (true);

create policy "anon select" on public.board_entries
  for select to anon, authenticated using (true);
