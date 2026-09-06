import { FileText } from "lucide-react";
import type { Source } from "../../../../data/mockData";
import "./SourceItem.css";

interface SourceItemProps {
  source: Source;
}

export default function SourceItem({ source }: SourceItemProps) {
  return (
    <div className="source">
      <FileText size={14} className="source-icon" />
      <span className="source-name">{source.name}</span>
      <span className={`status-dot status-${source.status}`} />
    </div>
  );
}
