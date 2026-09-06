import { Send } from "lucide-react";
import "./ChatInput.css";

interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
}

export default function ChatInput({ value, onChange, onSend }: ChatInputProps) {
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
