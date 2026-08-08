import MessageText from "./MessageText";
import CitationPanel from "./CitationPanel";
import StreamingTrace from "./StreamingTrace";

export default function Message({ message, openCitation, onToggleCitation }) {
  const activeCitation = message.citations?.find((c) => c.n === openCitation);

  return (
    <div className={`msg-row ${message.role}`}>
      <div className={`bubble ${message.role} ${message.streaming ? "streaming" : ""}`}>
        <MessageText
          text={message.text}
          citations={message.citations}
          onToggleCitation={onToggleCitation}
        />
        {activeCitation && <CitationPanel citation={activeCitation} />}
        {message.streaming && <StreamingTrace />}
      </div>
    </div>
  );
}
