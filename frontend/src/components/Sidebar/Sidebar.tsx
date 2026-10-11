import { useRef } from "react";
import type { ChangeEvent } from "react";
import { Plus } from "lucide-react";
import SourceItem from "../../features/chat/components/SourceItem/SourceItem";
import type { Source } from "../../features/chat/types";
import "./Sidebar.css";

interface SidebarProps {
  sources: Source[];
  onAddSource: (file: File) => void;
}

export default function Sidebar({ sources, onAddSource }: SidebarProps) {
  const fileInput = useRef<HTMLInputElement>(null);

  function handleChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) onAddSource(file);
    e.target.value = ""; // allow re-selecting the same file
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-label">Sources</div>
      {sources.map((s) => (
        <SourceItem key={s.id} source={s} />
      ))}
      <input
        ref={fileInput}
        type="file"
        accept=".pdf,.txt,application/pdf,text/plain"
        hidden
        onChange={handleChange}
      />
      <button className="add-source" onClick={() => fileInput.current?.click()}>
        <Plus size={13} /> add source
      </button>
    </aside>
  );
}
