"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { api } from "@/lib/api";
import type { DemoSummary } from "@/lib/types";

const fallback: DemoSummary = {
  id: "checkout-incident",
  title: "Checkout payment failures after deployment",
  suggested_question: "Why did checkout failures increase after the latest deployment?",
  occurred_at: "2026-08-19T10:14:00Z",
  source_count: 10,
  chunk_count: 10,
  source_types: {},
  relationship_count: 10,
};

export function LandingDemo() {
  const [demo, setDemo] = useState(fallback);

  useEffect(() => {
    api.demo().then(setDemo).catch(() => undefined);
  }, []);

  return (
    <section className="demoCase" aria-labelledby="demo-title">
      <div className="caseHeader">
        <span className="eyebrow">Built-in case · No API key</span>
        <span className="caseTime">19 Aug · 10:14 UTC</span>
      </div>
      <h2 id="demo-title">The checkout spike</h2>
      <p>{demo.title}. Ten minutes of evidence, assembled before the hypothesis.</p>
      <blockquote>“{demo.suggested_question}”</blockquote>
      <div className="sourceStrip" aria-label="Indexed source summary">
        <span><b>{demo.source_count}</b> sources</span>
        <span><b>{demo.chunk_count}</b> chunks</span>
        <span><b>{demo.relationship_count}</b> links</span>
      </div>
      <Link className="primaryButton" href="/investigations/demo">
        Investigate Demo Incident <span aria-hidden="true">→</span>
      </Link>
      <p className="microcopy">Free deterministic demo · Same pipeline as the implemented OpenAI and Gemini providers.</p>
    </section>
  );
}

