export const mockSources = [
  { id: 1, name: "design-doc.md", status: "ready" },
  { id: 2, name: "api-notes.pdf", status: "ready" },
  { id: 3, name: "meeting-transcript.txt", status: "processing" },
];

export const mockMessages = [
  {
    id: 1,
    role: "user",
    text: "What chunking strategy does the ingestion pipeline use?",
  },
  {
    id: 2,
    role: "assistant",
    text: "The pipeline uses fixed-size chunking with 10 to 15 percent overlap [1]. Semantic chunking is noted as a possible upgrade, to be documented if adopted [2].",
    citations: [
      { n: 1, source: "design-doc.md", snippet: "Chunking strategy: fixed-size with ~10-15% overlap to start" },
      { n: 2, source: "design-doc.md", snippet: "document if you switch to semantic chunking and why" },
    ],
  },
  { id: 3, role: "user", text: "And how is retrieval scored?" },
  {
    id: 4,
    role: "assistant",
    text: "Cosine similarity, top-k with k=4 to 6 to start.",
    streaming: true,
  },
];
