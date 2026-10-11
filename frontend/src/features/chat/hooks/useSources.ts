import { useEffect, useState } from "react";
import type { Source } from "../types";
import { listDocuments, uploadDocument, waitForDocumentStatus } from "../api/documentsApi";

export function useSources() {
  const [sources, setSources] = useState<Source[]>([]);

  useEffect(() => {
    let cancelled = false;
    listDocuments()
      .then((docs) => {
        if (cancelled) return;
        const loaded: Source[] = docs.map((d) => ({
          id: d.id,
          name: d.filename,
          status: d.status === "processed" || d.status === "failed" ? d.status : "processing",
          error: d.status === "failed" ? "Processing failed" : undefined,
        }));
        // Keep anything uploaded locally while the request was in flight.
        setSources((local) => [
          ...loaded,
          ...local.filter((s) => !loaded.some((l) => l.id === s.id)),
        ]);
      })
      .catch(() => {
        // Backend unreachable: leave the list as-is rather than failing the app.
      });
    return () => {
      cancelled = true;
    };
  }, []);

  function updateSource(id: string, patch: Partial<Source>) {
    setSources((list) => list.map((s) => (s.id === id ? { ...s, ...patch } : s)));
  }

  async function addSource(file: File) {
    const localId = crypto.randomUUID();
    setSources((list) => [...list, { id: localId, name: file.name, status: "processing" }]);

    try {
      const doc = await uploadDocument(file);
      updateSource(localId, { id: doc.id });
      const status = await waitForDocumentStatus(doc.id);
      updateSource(doc.id, {
        status,
        error: status === "failed" ? "Processing failed" : undefined,
      });
    } catch (e) {
      updateSource(localId, {
        status: "error",
        error: e instanceof Error ? e.message : "Upload failed",
      });
    }
  }

  return { sources, addSource };
}
