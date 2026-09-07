import { useState } from "react";
import type { Message } from "../types";
import { streamChat } from "../api/chatApi";

export function useChatStream(initialMessages: Message[]) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [openCitation, setOpenCitation] = useState<number | null>(null);

  function handleSend() {
    if (!input.trim()) return;
    setMessages((m) => [...m, { id: Date.now(), role: "user", text: input }]);
    handleStream();
    setInput("");
  }

  async function handleStream() {
    const message = input;
    const assistantId = Date.now();

    setMessages((m) => [...m, { id: assistantId, role: "assistant", text: "" }]);

    for await (const chunk of streamChat(message)) {
      setMessages((m) =>
        m.map((msg) =>
          msg.id === assistantId ? { ...msg, text: msg.text + chunk } : msg
        )
      );
    }
  }
  function toggleCitation(n: number) {
    setOpenCitation((current) => (current === n ? null : n));
  }

  return { input, setInput, messages, openCitation, handleSend, toggleCitation };
}
