import { Plus } from "lucide-react";
import SourceItem from "../../features/chat/components/SourceItem/SourceItem";
import type { Source } from "../../data/mockData";
import "./Sidebar.css";

interface SidebarProps {
  sources: Source[];
}

export default function Sidebar({ sources }: SidebarProps) {
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
