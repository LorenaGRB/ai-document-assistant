import type { Citation } from "../../types";
import "./CitationPanel.css";

interface CitationPanelProps {
  citation?: Citation;
}

export default function CitationPanel({ citation }: CitationPanelProps) {
  if (!citation) return null;

  return (
    <div className="citation-panel">
      <div className="citation-panel-source">
        [{citation.n}] {citation.source}
      </div>
      "{citation.snippet}"
    </div>
  );
}
