import Link from "next/link";

import { LandingDemo } from "@/components/landing-demo";
import { SiteFooter } from "@/components/site-footer";

export default function Home() {
  return (
    <>
      <main>
        <section className="hero">
          <div className="heroCopy">
            <span className="eyebrow">AI investigation for deployment failures</span>
            <h1>Your app broke after a deployment.<br />Find out why.</h1>
            <p>IncidentLens investigates the logs, source code, recent commits, deployments, and previous incidents—then returns the most likely root cause with the evidence behind it.</p>
            <div className="heroActions"><Link className="primaryButton" href="/investigations/demo">Investigate Demo Incident <span>→</span></Link><Link className="textLink" href="/architecture">See how it works</Link></div>
            <ul className="trustList"><li><span>01</span>Connect the failure to the change</li><li><span>02</span>Open the evidence for every claim</li><li><span>03</span>Try the hosted demo without an API key</li></ul>
          </div>
          <LandingDemo />
        </section>

        <section className="howItWorks" aria-labelledby="how-heading">
          <div><span className="eyebrow">What happens under the hood</span><h2 id="how-heading">A causal path you can inspect.</h2></div>
          <ol>
            <li><span>01</span><h3>Index the incident</h3><p>Normalize code, logs, commits, releases, issues, and history into cited evidence.</p></li>
            <li><span>02</span><h3>Retrieve, then correct</h3><p>Fuse vector and BM25 ranks. If evidence is weak, rewrite and search again.</p></li>
            <li><span>03</span><h3>Verify the hypothesis</h3><p>Expand causal links, expose contradictions, and reject unsupported citations.</p></li>
          </ol>
        </section>

        <section className="proofSection">
          <div className="proofQuote"><span className="eyebrow">The output</span><blockquote>“Deployment → commit → contract violation → first error.”</blockquote><p>Not a magic answer. An evidence trail with a confidence boundary.</p></div>
          <div className="proofLinks"><Link href="/evaluation"><span>Measured retrieval</span><b>Dense vs hybrid vs full pipeline →</b></Link><Link href="/under-the-hood"><span>Verified implementation</span><b>See where each AI component runs →</b></Link></div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}

