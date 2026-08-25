"use client";

import Link from "next/link";
import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";

import { ApiError, api } from "@/lib/api";
import type { EvidenceKind, Investigation } from "@/lib/types";
import { EvidenceInspector } from "./evidence-inspector";

const suggestedQuestion = "Why did checkout failures increase after the latest deployment?";

const sourceLabels: Record<EvidenceKind, string> = {
  source_code: "Code",
  log: "Logs",
  commit: "Commits",
  deployment: "Deployments",
  release_note: "Releases",
  issue: "Issues",
  incident: "Prior incidents",
  documentation: "Docs",
};

export function InvestigationWorkspace({ initialId }: { initialId: string }) {
  const [question, setQuestion] = useState(suggestedQuestion);
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(initialId === "demo");
  const [error, setError] = useState<string | null>(null);

  const run = useCallback(async (nextQuestion: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await api.investigate(nextQuestion);
      setInvestigation(result);
      setSelectedId(result.report.supporting_evidence[0]?.evidence_id ?? result.evidence[0]?.evidence.id);
      window.history.replaceState(null, "", `/investigations/${result.id}`);
    } catch (caught) {
      const suffix = caught instanceof ApiError && caught.requestId ? ` · Request ${caught.requestId}` : "";
      setError(`${caught instanceof Error ? caught.message : "Investigation failed"}${suffix}`);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (initialId === "demo") {
      const timer = window.setTimeout(() => void run(suggestedQuestion), 0);
      return () => window.clearTimeout(timer);
    }
    api.investigation(initialId)
      .then((result) => {
        setInvestigation(result);
        setQuestion(result.question);
        setSelectedId(result.report.supporting_evidence[0]?.evidence_id ?? null);
      })
      .catch(() => setError("This process-local investigation expired. Run the case again to rebuild it from evidence."))
      .finally(() => setLoading(false));
    return undefined;
  }, [initialId, run]);

  const selected = useMemo(
    () => investigation?.evidence.find((item) => item.evidence.id === selectedId)?.evidence,
    [investigation, selectedId],
  );

  function submit(event: FormEvent) {
    event.preventDefault();
    if (question.trim().length >= 3) void run(question.trim());
  }

  return (
    <main className="workspaceShell">
      <header className="incidentHeader">
        <div>
          <span className="eyebrow">INC-2026-0819 · checkout-api</span>
          <h1>Checkout failure investigation</h1>
        </div>
        <div className="headerState"><span className={loading ? "pulse" : ""} /> {loading ? "Investigating" : investigation ? "Report ready" : "Ready"}</div>
      </header>

      <div className="workspaceGrid">
        <aside className="sourceRail" aria-label="Evidence sources">
          <span className="railTitle">Sources</span>
          {Object.entries(sourceLabels).map(([kind, label]) => {
            const count = investigation?.evidence.filter((item) => item.evidence.kind === kind).length ?? 0;
            return <div className="sourceType" key={kind}><span>{label}</span><b>{count || "·"}</b></div>;
          })}
          <Link href="/architecture" className="railLink">How retrieval works →</Link>
        </aside>

        <section className="investigationPane" aria-label="Investigation report">
          <form className="questionBox" onSubmit={submit}>
            <label htmlFor="question">Investigation question</label>
            <div>
              <input id="question" value={question} onChange={(event) => setQuestion(event.target.value)} maxLength={500} />
              <button disabled={loading || question.trim().length < 3} type="submit">{loading ? "Running…" : "Investigate"}</button>
            </div>
          </form>

          <div aria-live="polite">
            {loading && <InvestigationSkeleton />}
            {error && (
              <section className="errorState" role="alert">
                <h2>Couldn’t load this investigation</h2>
                <p>{error}</p>
                <button onClick={() => void run(suggestedQuestion)}>Rebuild from the demo evidence</button>
              </section>
            )}
            {investigation && !loading && (
              <>
                <article className="rootCauseCard">
                  <div className="resultLabel"><span>Likely root cause</span><b>{investigation.report.confidence} confidence · {Math.round(investigation.report.confidence_score * 100)}%</b></div>
                  <h2>{investigation.report.likely_root_cause}</h2>
                  <div className="resultMeta"><span>Affected service</span><b>{investigation.report.affected_service}</b><span>Relevant commit</span><b>{investigation.report.relevant_commits[0] || "Not established"}</b></div>
                </article>

                <section className="evidenceTrail" aria-labelledby="evidence-heading">
                  <div className="sectionHeading"><div><span className="eyebrow">Provenance</span><h2 id="evidence-heading">Evidence trail</h2></div><span>{investigation.report.supporting_evidence.length} verified claims</span></div>
                  {investigation.report.supporting_evidence.map((citation, index) => {
                    const item = investigation.evidence.find((entry) => entry.evidence.id === citation.evidence_id);
                    if (!item) return null;
                    return (
                      <button className={selectedId === citation.evidence_id ? "evidenceRow selected" : "evidenceRow"} key={citation.evidence_id} onClick={() => setSelectedId(citation.evidence_id)}>
                        <span className="evidenceIndex">0{index + 1}</span>
                        <span><b>{citation.claim}</b><small>{item.evidence.title} · {item.evidence.source_path}</small></span>
                        <span className="verified">Verified</span>
                      </button>
                    );
                  })}
                </section>

                {investigation.report.contradictions.length > 0 && (
                  <section className="contradictions">
                    <span className="eyebrow">Alternative checked</span>
                    <h2>Contradicting evidence</h2>
                    {investigation.report.contradictions.map((item) => (
                      <button key={item.evidence_id} onClick={() => setSelectedId(item.evidence_id)}>{item.claim}</button>
                    ))}
                  </section>
                )}

                <section className="timeline" aria-labelledby="timeline-heading">
                  <span className="eyebrow">Sequence</span><h2 id="timeline-heading">Incident timeline</h2>
                  <ol>
                    {investigation.report.timeline.map((event) => (
                      <li key={event.evidence_id}><time>{new Date(event.occurred_at).toLocaleTimeString([], {hour: "2-digit", minute: "2-digit", timeZone: "UTC"})} UTC</time><button onClick={() => setSelectedId(event.evidence_id)}>{event.label}</button></li>
                    ))}
                  </ol>
                </section>

                <details className="agentTrace">
                  <summary>Inspect LangGraph runtime · {investigation.trace.length} steps</summary>
                  <ol>{investigation.trace.map((step, index) => <li key={`${step.node}-${index}`}><b>{step.node.replaceAll("_", " ")}</b><span>{step.summary}</span><small>{step.duration_ms.toFixed(1)} ms · pass {step.attempt}</small></li>)}</ol>
                </details>
              </>
            )}
          </div>
        </section>

        <EvidenceInspector evidence={selected} />
      </div>
    </main>
  );
}

function InvestigationSkeleton() {
  return (
    <section className="loadingState" aria-label="Investigation in progress">
      <div className="loadingTop"><span className="spinner" aria-hidden="true" /><div><b>Building the evidence trail</b><p>Dense + BM25 retrieval, graph expansion, then claim verification.</p></div></div>
      {["Analyze and plan", "Retrieve and grade", "Expand and verify"].map((label, index) => <div className="loadingStep" key={label}><span>{index + 1}</span><p>{label}</p><i /></div>)}
    </section>
  );
}
