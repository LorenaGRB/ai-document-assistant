import type { Citation } from "../../types";
import "./MessageText.css";

interface MessageTextProps {
  text: string;
  citations?: Citation[];
  onToggleCitation: (n: number) => void;
}

export default function MessageText({ text, citations, onToggleCitation }: MessageTextProps) {
  if (!citations) return text;

  return text.split(/(\[\d+\])/g).map((part, i) => {
    const match = part.match(/\[(\d+)\]/);
    if (!match) return <span key={i}>{part}</span>;

    const n = Number(match[1]);
    return (
      <button key={i} className="citation-chip" onClick={() => onToggleCitation(n)}>
        {n}
      </button>
    );
  });
}
