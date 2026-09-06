/**
 * Mirrors the backend contract at POST /chat (app/api/routers/chat.py),
 * which streams a text/event-stream response. Not yet wired into the UI —
 * the chat screen still runs on local mock state.
 */
export async function streamChat(message: string): Promise<Response> {
  return fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });
}
