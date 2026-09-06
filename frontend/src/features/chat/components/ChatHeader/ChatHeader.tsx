import "./ChatHeader.css";

interface ChatHeaderProps {
  title: string;
}

export default function ChatHeader({ title }: ChatHeaderProps) {
  return (
    <div className="header">
      <span className="header-title">{title}</span>
      <span className="header-live">
        <span className="live-dot" /> live
      </span>
    </div>
  );
}
