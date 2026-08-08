import { Plus } from "lucide-react";
import SourceItem from "./SourceItem";

export default function Sidebar({ sources }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-label">Sources</div>
      {sources.map((s) => (
        <SourceItem key={s.id} source={s} />
      ))}
      <button className="add-source">
        <Plus size={13} /> add source
      </button>
    </aside>
  );
}
