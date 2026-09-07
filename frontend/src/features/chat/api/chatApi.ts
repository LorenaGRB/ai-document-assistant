/**
 * Mirrors the backend contract at POST /chat (app/api/routers/chat.py),
 * which streams a text/event-stream response. Not yet wired into the UI —
 * the chat screen still runs on local mock state.
 */
export async function* streamChat(message: string): AsyncGenerator<string> {
  const response = await fetch("http://127.0.0.1:8000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  //getReader comes from the Streams API. It allows you to read a stream of data in chunks. 
  const reader = response.body!.getReader();
  // TextDecoder is a built-in JavaScript class that allows you to decode a stream of bytes into a string.
  const decoder = new TextDecoder();

  while (true) {
    // Read a chunk of data from the stream. The read() method returns a promise that resolves to an object with two properties: value (the chunk of data) and done (a boolean indicating whether the stream has ended).
    const { value, done } = await reader.read();
    if (done) break;
    // Decode the chunk of data into a string and yield it to the caller of the generator function. The stream option is set to true to indicate that this is a streaming operation.
    yield decoder.decode(value, { stream: true });
  }
}