export type Role = "user" | "assistant";

export interface Citation {
  n: number;
  source: string;
  snippet: string;
}

export interface Message {
  id: number;
  role: Role;
  text: string;
  citations?: Citation[];
  streaming?: boolean;
}

export interface Source {
  id: string;
  name: string;
  status: "processing" | "processed" | "failed" | "error";
  /** Shown when status is "error" (upload rejected) or "failed" (processing failed). */
  error?: string;
}
