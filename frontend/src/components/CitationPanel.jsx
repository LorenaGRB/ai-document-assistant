export default function CitationPanel({ citation }) {
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
