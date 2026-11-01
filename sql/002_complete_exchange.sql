-- Completes one question/answer exchange atomically:
-- marks the user's question as completed and inserts the assistant's answer.
-- Both writes happen inside the same function call, so they succeed or fail together.

create or replace function complete_exchange(
  p_question_id uuid,
  p_conversation_id uuid,
  p_content text
)
returns messages
language plpgsql
set search_path = public
as $$
declare
  v_response messages;
begin
  update messages
     set status = 'completed'
   where id = p_question_id
     and conversation_id = p_conversation_id
     and status = 'new';

  if not found then
    raise exception 'Question % is not pending in conversation %',
      p_question_id, p_conversation_id;
  end if;

  insert into messages (conversation_id, role, content, status)
  values (p_conversation_id, 'assistant', p_content, 'completed')
  returning * into v_response;

  return v_response;
end;
$$;

-- Only the backend (secret key = service_role) may call it through the API.
revoke execute on function complete_exchange(uuid, uuid, text)
  from public, anon, authenticated;
grant execute on function complete_exchange(uuid, uuid, text)
  to service_role;
