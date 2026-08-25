import type { Metadata } from "next";
import Link from "next/link";

import { SiteFooter } from "@/components/site-footer";

export const metadata: Metadata = { title: "About" };

export default function AboutPage() {
  return <><main className="contentPage aboutPage"><header className="pageHero"><span className="eyebrow">About IncidentLens</span><h1>Calm software for<br /><em>uncertain moments.</em></h1><p>IncidentLens is a portfolio-scale investigation system built around one idea: an answer is only as useful as the evidence trail behind it.</p></header><section className="aboutGrid"><article><span>01</span><h2>The problem</h2><p>During an incident, logs, code, deployments, issues, and history sit in different places. Responders reconstruct the sequence manually while plausible AI summaries can hide what is missing.</p></article><article><span>02</span><h2>The stance</h2><p>IncidentLens returns a ranked hypothesis with citations, contradictions, confidence, and limitations. It does not promise certainty, execute code, or remediate production.</p></article><article><span>03</span><h2>The proof</h2><p>The checkout demo runs a real ingestion, hybrid retrieval, graph, LangGraph, provider, and verification pipeline. Its benchmark and source are inspectable.</p></article></section><div className="aboutCta"><h2>Start with the evidence.</h2><Link className="primaryButton" href="/investigations/demo">Run the checkout investigation →</Link></div></main><SiteFooter /></>;
}

