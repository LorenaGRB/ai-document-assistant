import { FileText } from "lucide-react";
import type { Source } from "../../types";
import "./SourceItem.css";

interface SourceItemProps {
  source: Source;
}

export default function SourceItem({ source }: SourceItemProps) {
  const hasError = source.status === "error" || source.status === "failed";
  return (
    <div className={`source${hasError ? " source-has-error" : ""}`}>
      <FileText size={14} className="source-icon" />
      <div className="source-body">
        <span className="source-name" title={source.name}>{source.name}</span>
        {hasError && source.error && (
          <span className="source-error" role="alert">{source.error}</span>
        )}
      </div>
      <span className={`status-dot status-${source.status}`} title={source.status} />
    </div>
  );
}
