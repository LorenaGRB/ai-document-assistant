import Message from "../Message/Message";
import type { Message as MessageType } from "../../types";
import "./ChatThread.css";
import { useEffect, useRef } from "react";

interface ChatThreadProps {
  messages: MessageType[];
  openCitation: number | null;
  onToggleCitation: (n: number) => void;
}

export default function ChatThread({ messages, openCitation, onToggleCitation }: ChatThreadProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);
  
  return (
    <div className="thread">
      {messages.map((m) => (
        <Message
          key={m.id}
          message={m}
          openCitation={openCitation}
          onToggleCitation={onToggleCitation}
        />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
