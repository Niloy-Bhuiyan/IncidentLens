import type { Metadata } from "next";
import Link from "next/link";

import { SiteFooter } from "@/components/site-footer";

export const metadata: Metadata = { title: "Under the Hood" };

const repository = "https://github.com/Niloy-Bhuiyan/IncidentLens/blob/main";

const implementation = [
  {
    title: "Python / FastAPI",
    body: "A typed Python API owns ingestion, investigation, provider selection, validation, security middleware, and the public OpenAPI contract.",
    path: "backend/app/main.py",
    href: `${repository}/backend/app/main.py`,
  },
  {
    title: "LangChain + data preparation",
    body: "Runtime ingestion validates controlled files, cleans and normalizes them, creates LangChain Documents, preserves metadata, and chunks them before indexing.",
    path: "backend/app/ingestion/pipeline.py",
    href: `${repository}/backend/app/ingestion/pipeline.py`,
  },
  {
    title: "LangGraph workflow",
    body: "A compiled state graph—not a diagram-only wrapper—controls planning, retrieval, evidence grading, conditional query correction, synthesis, citation verification, and report construction.",
    path: "backend/app/agents/graph.py",
    href: `${repository}/backend/app/agents/graph.py`,
  },
  {
    title: "Hybrid RAG",
    body: "Independent vector and BM25 rankings are fused with reciprocal-rank fusion, then reranked with bounded source, error-signature, change-intent, and graph signals.",
    path: "backend/app/retrieval/engine.py",
    href: `${repository}/backend/app/retrieval/engine.py`,
  },
  {
    title: "Evidence graph",
    body: "Typed edges connect error → service → source file → commit → deployment → prior incident. Those links add relevant evidence after first-pass retrieval.",
    path: "backend/app/graph/evidence_graph.py",
    href: `${repository}/backend/app/graph/evidence_graph.py`,
  },
  {
    title: "Versioned prompts",
    body: "Planner, grader, rewriter, synthesis, and verifier prompts are versioned on disk. Retrieved text is labeled as untrusted data and citations must use supplied IDs.",
    path: "backend/app/prompts/",
    href: `${repository}/backend/app/prompts`,
  },
];

const providers = [
  ["OpenAI provider", "Official async OpenAI SDK · structured Pydantic output · timeout · retries · safe errors", "backend/app/llm/openai_provider.py"],
  ["Gemini provider", "Official Google GenAI SDK · JSON schema output · timeout · safe errors", "backend/app/llm/gemini_provider.py"],
  ["Deterministic demo provider", "Evidence-derived, zero-credit output for this public demo and repeatable tests", "backend/app/llm/mock_provider.py"],
];

export default function UnderTheHoodPage() {
  return (
    <><main className="contentPage underHoodPage">
      <header className="pageHero">
        <span className="eyebrow">Verified AI engineering</span>
        <h1>What runs.<br /><em>Where it runs.</em></h1>
        <p>This is the implementation map behind the demo. Each claim below points to the runtime source that performs the work; boundaries are stated as plainly as capabilities.</p>
        <div className="pageActions"><a className="primaryButton" href="https://incidentlens-api-delta.vercel.app/docs">Open the live API contract →</a><Link className="textLink" href="/evaluation">Inspect the benchmark</Link></div>
      </header>

      <section className="implementationGrid" aria-label="AI engineering implementation map">
        {implementation.map((item, index) => <article key={item.title}><span>{String(index + 1).padStart(2, "0")}</span><h2>{item.title}</h2><p>{item.body}</p><a href={item.href}><code>{item.path}</code> ↗</a></article>)}
      </section>

      <section className="vectorBoundary">
        <div><span className="eyebrow">Vector storage, accurately stated</span><h2>Real vectors. In-process store.</h2></div>
        <p>The hosted demo computes 384-dimensional deterministic feature-hash embeddings through the LangChain embeddings interface and performs cosine search over an in-memory Python index. It is genuine vector retrieval, but it is not a managed vector database and not a neural embedding model. PostgreSQL + pgvector is a documented scale path, not a deployed claim.</p>
      </section>

      <section className="providerSection" aria-labelledby="provider-heading">
        <div><span className="eyebrow">Model integration</span><h2 id="provider-heading">One pipeline, three explicit providers.</h2><p>The hosted site defaults to deterministic/free mode so visitors can run it without consuming paid credits. Selecting a real provider runs the same retrieval and LangGraph path through the implemented adapter; missing credentials fail safely rather than silently falling back.</p></div>
        <ol>{providers.map(([name, detail, path]) => <li key={name}><h3>{name}</h3><p>{detail}</p><a href={`${repository}/${path}`}><code>{path}</code> ↗</a></li>)}</ol>
      </section>

      <section className="dataPath" aria-labelledby="data-path-heading"><span className="eyebrow">Data preparation</span><h2 id="data-path-heading">Parse → clean → normalize → chunk → metadata → embed → index</h2><p>Ground-truth answers live outside the indexed demo corpus. The evaluation runner rebuilds the index from source and compares dense-only, hybrid, and graph-expanded full-pipeline retrieval.</p></section>
    </main><SiteFooter /></>
  );
}
