create table if not exists public.highlights (
  id uuid default gen_random_uuid() primary key,
  user_key text not null,
  document_id text not null,
  payload jsonb not null default '[]'::jsonb,
  updated_at timestamp with time zone default now(),
  unique(user_key, document_id)
);

create or replace function public.set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists set_highlights_updated_at on public.highlights;

create trigger set_highlights_updated_at
before update on public.highlights
for each row
execute function public.set_updated_at();

alter table public.highlights enable row level security;

drop policy if exists "allow anon read highlights" on public.highlights;
drop policy if exists "allow anon insert highlights" on public.highlights;
drop policy if exists "allow anon update highlights" on public.highlights;
drop policy if exists "allow anon delete highlights" on public.highlights;

create policy "allow anon read highlights"
on public.highlights
for select
to anon
using (true);

create policy "allow anon insert highlights"
on public.highlights
for insert
to anon
with check (true);

create policy "allow anon update highlights"
on public.highlights
for update
to anon
using (true)
with check (true);

create policy "allow anon delete highlights"
on public.highlights
for delete
to anon
using (true);
