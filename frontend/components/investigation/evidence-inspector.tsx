import Link from "next/link";

import type { Evidence } from "@/lib/types";

export function EvidenceInspector({ evidence }: { evidence?: Evidence }) {
  if (!evidence) {
    return (
      <aside className="inspector emptyInspector" aria-label="Evidence inspector">
        <span className="eyebrow">Evidence inspector</span>
        <p>Select a cited item to inspect its source and metadata.</p>
      </aside>
    );
  }

  return (
    <aside className="inspector" aria-label="Evidence inspector">
      <div className="inspectorHeading">
        <span className={`kindTag kind-${evidence.kind}`}>{evidence.kind.replace("_", " ")}</span>
        <Link href={`/evidence/${evidence.id}`}>Open full source ↗</Link>
      </div>
      <h2>{evidence.title}</h2>
      <p className="sourcePath">{evidence.source_path}</p>
      <pre tabIndex={0}><code>{evidence.content}</code></pre>
      <dl className="metadataList">
        {Object.entries(evidence.metadata).slice(0, 6).map(([key, value]) => (
          <div key={key}>
            <dt>{key.replaceAll("_", " ")}</dt>
            <dd>{typeof value === "string" ? value : JSON.stringify(value)}</dd>
          </div>
        ))}
      </dl>
    </aside>
  );
}

