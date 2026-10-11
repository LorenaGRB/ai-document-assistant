const BASE_URL = "http://127.0.0.1:8000";

export interface UploadedDocument {
  id: string;
  filename: string;
  status: string;
}

/** GET /documents (newest first). */
export async function listDocuments(): Promise<UploadedDocument[]> {
  const response = await fetch(`${BASE_URL}/documents`);
  if (!response.ok) throw new Error(`Failed to load documents (${response.status})`);
  return response.json();
}

/** POST /documents (app/api/routers/documents.py). Throws Error with a user-facing message on failure. */
export async function uploadDocument(file: File): Promise<UploadedDocument> {
  const body = new FormData();
  body.append("file", file);

  let response: Response;
  try {
    response = await fetch(`${BASE_URL}/documents`, { method: "POST", body });
  } catch {
    throw new Error("Could not reach the server");
  }

  if (response.status === 400) throw new Error("Unsupported file type (PDF or text only)");
  if (response.status === 409) throw new Error("A document with this name already exists");
  if (!response.ok) throw new Error(`Upload failed (${response.status})`);

  return response.json();
}

/**
 * GET /documents/{id}/status. The backend streams the bare status string
 * ("processed" | "failed") without SSE framing, so EventSource can't parse it;
 * read it with fetch streaming instead.
 */
export async function waitForDocumentStatus(id: string): Promise<"processed" | "failed"> {
  try {
    const response = await fetch(`${BASE_URL}/documents/${id}/status`);
    if (!response.ok || !response.body) return "failed";

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let text = "";
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      text += decoder.decode(value, { stream: true });
      if (text.includes("processed")) return "processed";
      if (text.includes("failed")) return "failed";
    }
  } catch {
    // fall through
  }
  return "failed";
}
