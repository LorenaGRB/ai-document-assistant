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
