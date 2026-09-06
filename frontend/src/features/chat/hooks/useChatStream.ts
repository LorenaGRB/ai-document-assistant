import { useState } from "react";
import type { Message } from "../types";

export function useChatStream(initialMessages: Message[]) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [openCitation, setOpenCitation] = useState<number | null>(null);

  function handleSend() {
    if (!input.trim()) return;
    setMessages((m) => [...m, { id: Date.now(), role: "user", text: input }]);
    setInput("");
  }

  function toggleCitation(n: number) {
    setOpenCitation((current) => (current === n ? null : n));
  }

  return { input, setInput, messages, openCitation, handleSend, toggleCitation };
}
