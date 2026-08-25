import type { Metadata } from "next";

import { SiteFooter } from "@/components/site-footer";
import { api } from "@/lib/api";

export const metadata: Metadata = { title: "Retrieval evaluation" };

const labels = { dense: "Dense baseline", hybrid: "Hybrid retrieval", full_pipeline: "Full pipeline" } as const;

export default async function EvaluationPage() {
  const result = await api.evaluation().catch(() => null);
  return (
    <><main className="contentPage"><header className="pageHero"><span className="eyebrow">Reproducible evidence</span><h1>Retrieval, measured.<br /><em>Not marketed.</em></h1><p>The seeded benchmark compares independent vector search, BM25-fused hybrid retrieval, and graph-expanded reranking against committed ground truth.</p></header>{result ? <><section className="benchmarkIntro"><div><span>Dataset</span><b>retrieval-v{result.dataset_version}</b></div><div><span>Queries</span><b>{result.query_count}</b></div><div><span>Embedding</span><b>{result.embedding}</b></div><div><span>Fusion</span><b>{result.fusion}</b></div></section><section className="benchmarkTable" aria-labelledby="benchmark-heading"><div className="sectionHeading"><div><span className="eyebrow">Latest generated run</span><h2 id="benchmark-heading">Top-5 retrieval quality</h2></div><time>{new Date(result.generated_at).toLocaleDateString("en-US", { dateStyle: "medium" })}</time></div><div role="table" aria-label="Retrieval benchmark"><div className="benchmarkRow benchmarkHeader" role="row"><span>Configuration</span><span>Recall@5</span><span>MRR</span><span>Coverage</span></div>{Object.entries(result.aggregate).map(([key, metrics]) => <div className="benchmarkRow" role="row" key={key}><strong>{labels[key as keyof typeof labels]}</strong><Metric value={metrics.recall_at_5} /><Metric value={metrics.mrr} /><Metric value={metrics.root_cause_evidence_coverage} /></div>)}</div></section><aside className="honestyNote"><span>What this proves</span><p>On four synthetic queries, hybrid retrieval improves Recall@5 from {(result.aggregate.dense.recall_at_5 * 100).toFixed(1)}% to {(result.aggregate.hybrid.recall_at_5 * 100).toFixed(1)}%. It does not prove general production accuracy.</p></aside></> : <section className="errorState"><h2>Benchmark unavailable</h2><p>Run <code>python -m backend.app.evaluation.runner</code> and restart the API.</p></section>}</main><SiteFooter /></>
  );
}

function Metric({ value }: { value: number }) { return <span className="metricCell"><b>{value.toFixed(3)}</b><i><span style={{width: `${value * 100}%`}} /></i></span>; }

