create table messages (
  id uuid primary key default gen_random_uuid(),
  conversation_id uuid not null,
  role text not null check (role in ('user', 'assistant')),
  content text not null,
  status text not null default 'new'
    check (status in ('new', 'completed', 'failed')),
  created_at timestamptz not null default now()
);

create index messages_conversation_idx
  on messages (conversation_id, created_at);

alter table messages enable row level security;