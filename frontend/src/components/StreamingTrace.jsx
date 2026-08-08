export default function StreamingTrace() {
  return (
    <div className="trace">
      {[0, 1, 2, 3, 4, 5].map((i) => (
        <span key={i} style={{ animationDelay: `${i * 0.12}s` }} />
      ))}
    </div>
  );
}
