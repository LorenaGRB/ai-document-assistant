import { FileText } from "lucide-react";

export default function SourceItem({ source }) {
  return (
    <div className="source">
      <FileText size={14} className="source-icon" />
      <span className="source-name">{source.name}</span>
      <span className={`status-dot status-${source.status}`} />
    </div>
  );
}
