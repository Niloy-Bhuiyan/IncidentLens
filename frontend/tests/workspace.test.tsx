import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { InvestigationWorkspace } from "@/components/investigation/workspace";
import type { Investigation } from "@/lib/types";

const investigation: Investigation = {
  id: "inv-demo",
  question: "Why did checkout fail?",
  status: "completed",
  created_at: "2026-08-19T10:20:00Z",
  completed_at: "2026-08-19T10:20:01Z",
  report: {
    likely_root_cause: "Deployment introduced a currency contract violation.",
    confidence: "High",
    confidence_score: 0.94,
    affected_service: "checkout-api",
    supporting_evidence: [{ evidence_id: "commit-a81d2c", claim: "The commit changed normalization.", supports: true }],
    contradictions: [],
    relevant_files: ["source/payment_service.py"],
    relevant_commits: ["a81d2c"],
    timeline: [{ occurred_at: "2026-08-19T10:00:00Z", label: "Deployment", evidence_id: "commit-a81d2c", kind: "commit" }],
    limitations: ["Hypothesis only"],
    provider: "mock",
    prompt_version: "root_cause/v1",
  },
  evidence: [{
    evidence: {
      id: "commit-a81d2c",
      source_id: "checkout-incident",
      kind: "commit",
      title: "Commit a81d2c",
      content: "currency normalization diff",
      source_path: "commits/a81d2c.json",
      metadata: { commit: "a81d2c" },
      content_hash: "hash",
      occurred_at: "2026-08-19T10:00:00Z",
    },
    score: 1,
    relationship: null,
    breakdown: { dense: 1, sparse: 1, fusion: 1, rerank: 1, graph: 0 },
  }],
  trace: [{ node: "synthesize_root_cause", status: "completed", duration_ms: 2.4, summary: "Built report", attempt: 1 }],
};

describe("InvestigationWorkspace", () => {
  it("runs the demo and renders cited evidence and trace", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => investigation }));
    vi.spyOn(window.history, "replaceState").mockImplementation(() => undefined);

    render(<InvestigationWorkspace initialId="demo" />);

    expect(screen.getByLabelText(/investigation in progress/i)).toBeInTheDocument();
    expect(await screen.findByText(investigation.report.likely_root_cause)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: /checkout payment requests started failing/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /the commit changed normalization/i })).toBeInTheDocument();
    expect(screen.getByText(/inspect langgraph runtime/i)).toBeInTheDocument();
    await waitFor(() => expect(window.history.replaceState).toHaveBeenCalled());
  });

  it("recovers from an API error with an actionable retry", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: false,
      status: 503,
      json: async () => ({ error: { code: "provider_unavailable", message: "Demo temporarily unavailable" } }),
    }));

    render(<InvestigationWorkspace initialId="demo" />);

    expect(await screen.findByRole("alert")).toHaveTextContent("Demo temporarily unavailable");
    expect(screen.getByRole("button", { name: /rebuild from the demo evidence/i })).toBeEnabled();
  });
});

