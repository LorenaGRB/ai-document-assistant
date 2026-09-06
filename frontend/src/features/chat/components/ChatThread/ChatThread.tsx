import Message from "../Message/Message";
import type { Message as MessageType } from "../../types";
import "./ChatThread.css";

interface ChatThreadProps {
  messages: MessageType[];
  openCitation: number | null;
  onToggleCitation: (n: number) => void;
}

export default function ChatThread({ messages, openCitation, onToggleCitation }: ChatThreadProps) {
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
    </div>
  );
}
