import Message from "./Message";

export default function ChatThread({ messages, openCitation, onToggleCitation }) {
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
