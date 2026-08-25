import Link from "next/link";
import { notFound } from "next/navigation";

import { SiteFooter } from "@/components/site-footer";
import { api } from "@/lib/api";

export default async function EvidencePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const result = await api.evidence(id).catch(() => null);
  if (!result) notFound();
  const { evidence, relations } = result;
  return (
    <><main className="contentPage evidencePage"><Link className="backLink" href="/investigations/demo">← Back to investigation</Link><header><span className={`kindTag kind-${evidence.kind}`}>{evidence.kind.replace("_", " ")}</span><h1>{evidence.title}</h1><p>{evidence.source_path}</p></header><section className="sourceDocument"><div><span>Source content</span><code>SHA-256 {evidence.content_hash.slice(0, 12)}…</code></div><pre><code>{evidence.content}</code></pre></section><div className="evidenceDetails"><section><span className="eyebrow">Metadata</span><dl className="metadataList">{Object.entries(evidence.metadata).map(([key, value]) => <div key={key}><dt>{key.replaceAll("_", " ")}</dt><dd>{typeof value === "string" ? value : JSON.stringify(value)}</dd></div>)}</dl></section><section><span className="eyebrow">Evidence graph</span><h2>{relations.length} direct relationships</h2><ul className="relationList">{relations.map((relation, index) => <li key={index}><b>{String(relation.type).replace("reverse:", "← ")}</b><Link href={`/evidence/${String(relation.target)}`}>{String(relation.target)}</Link></li>)}</ul></section></div></main><SiteFooter /></>
  );
}

