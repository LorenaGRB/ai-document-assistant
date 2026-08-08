import { Send } from "lucide-react";

export default function ChatInput({ value, onChange, onSend }) {
  return (
    <div className="input-row">
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && onSend()}
        placeholder="Ask about your documents..."
      />
      <button className="send-btn" onClick={onSend}>
        <Send size={16} />
      </button>
    </div>
  );
}
