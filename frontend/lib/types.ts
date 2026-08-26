export type EvidenceKind =
  | "source_code"
  | "log"
  | "commit"
  | "deployment"
  | "release_note"
  | "issue"
  | "incident"
  | "documentation";

export interface Evidence {
  id: string;
  source_id: string;
  kind: EvidenceKind;
  title: string;
  content: string;
  source_path: string;
  metadata: Record<string, unknown>;
  content_hash: string;
  occurred_at: string | null;
}

export interface RankedEvidence {
  evidence: Evidence;
  score: number;
  relationship: string | null;
  breakdown: { dense: number; sparse: number; fusion: number; rerank: number; graph: number };
}

export interface Citation {
  evidence_id: string;
  claim: string;
  supports: boolean;
}

export interface TraceStep {
  node: string;
  status: string;
  duration_ms: number;
  summary: string;
  attempt: number;
}

export interface Investigation {
  id: string;
  question: string;
  status: string;
  created_at: string;
  completed_at: string;
  report: {
    likely_root_cause: string;
    confidence: "High" | "Moderate" | "Low";
    confidence_score: number;
    affected_service: string;
    supporting_evidence: Citation[];
    contradictions: Citation[];
    relevant_files: string[];
    relevant_commits: string[];
    timeline: Array<{ occurred_at: string; label: string; evidence_id: string; kind: string }>;
    limitations: string[];
    provider: string;
    prompt_version: string;
  };
  evidence: RankedEvidence[];
  trace: TraceStep[];
}

export interface DemoSummary {
  id: string;
  title: string;
  suggested_question: string;
  occurred_at: string;
  source_count: number;
  chunk_count: number;
  source_types: Record<string, number>;
  relationship_count: number;
}

export interface EvaluationResult {
  schema_version: string;
  dataset_version: string;
  generated_at: string;
  query_count: number;
  retrieval_query_count: number;
  insufficient_evidence_query_count: number;
  categories: string[];
  k: number;
  embedding: string;
  fusion: string;
  aggregate: Record<
    "dense" | "hybrid" | "full_pipeline",
    {
      recall_at_5: number;
      precision_at_5: number;
      mrr: number;
      evidence_hit_rate: number;
      root_cause_evidence_coverage: number;
      abstention_accuracy: number;
    }
  >;
}

