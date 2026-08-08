export default function ChatHeader({ title }) {
  return (
    <div className="header">
      <span className="header-title">{title}</span>
      <span className="header-live">
        <span className="live-dot" /> live
      </span>
    </div>
  );
}
