import MessageText from "../MessageText/MessageText";
import CitationPanel from "../CitationPanel/CitationPanel";
import StreamingTrace from "../StreamingTrace/StreamingTrace";
import type { Message as MessageType } from "../../types";
import "./Message.css";

interface MessageProps {
  message: MessageType;
  openCitation: number | null;
  onToggleCitation: (n: number) => void;
}

export default function Message({ message, openCitation, onToggleCitation }: MessageProps) {
  const activeCitation = message.citations?.find((c) => c.n === openCitation);

  return (
    <div className={`msg-row ${message.role}`}>
      <div className={`bubble ${message.role} ${message.streaming ? "streaming" : ""}`}>
        <MessageText
          text={message.text}
          // citations={message.citations}
          // onToggleCitation={onToggleCitation}
        />
        {activeCitation && <CitationPanel citation={activeCitation} />}
        {message.streaming && <StreamingTrace />}
      </div>
    </div>
  );
}
