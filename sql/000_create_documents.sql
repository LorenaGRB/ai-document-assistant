create table documents (
  id uuid primary key default gen_random_uuid(),
  filename text not null,
  storage_path text not null,
  status text not null default 'processing',
  created_at timestamptz not null default now()
);

alter table documents enable row level security;