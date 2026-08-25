import Link from "next/link";

import { LandingDemo } from "@/components/landing-demo";
import { SiteFooter } from "@/components/site-footer";

export default function Home() {
  return (
    <>
      <main>
        <section className="hero">
          <div className="heroCopy">
            <span className="eyebrow">Evidence-first incident investigation</span>
            <h1>Find the change<br />behind the failure.</h1>
            <p>IncidentLens connects logs, source, commits, deployments, and prior incidents into a root-cause hypothesis you can inspect—not merely trust.</p>
            <div className="heroActions"><Link className="primaryButton" href="/investigations/demo">Investigate the demo <span>→</span></Link><Link className="textLink" href="/architecture">See the system design</Link></div>
            <ul className="trustList"><li><span>01</span>Every claim cites source evidence</li><li><span>02</span>Corrective retrieval is visible</li><li><span>03</span>No paid model required</li></ul>
          </div>
          <LandingDemo />
        </section>

        <section className="howItWorks" aria-labelledby="how-heading">
          <div><span className="eyebrow">Investigation, not chat</span><h2 id="how-heading">A causal path, assembled in public.</h2></div>
          <ol>
            <li><span>01</span><h3>Index the incident</h3><p>Normalize code, logs, commits, releases, issues, and history into cited evidence.</p></li>
            <li><span>02</span><h3>Retrieve, then correct</h3><p>Fuse vector and BM25 ranks. If evidence is weak, rewrite and search again.</p></li>
            <li><span>03</span><h3>Verify the hypothesis</h3><p>Expand causal links, expose contradictions, and reject unsupported citations.</p></li>
          </ol>
        </section>

        <section className="proofSection">
          <div className="proofQuote"><span className="eyebrow">The output</span><blockquote>“Deployment → commit → contract violation → first error.”</blockquote><p>Not a magic answer. An evidence trail with a confidence boundary.</p></div>
          <div className="proofLinks"><Link href="/evaluation"><span>Measured retrieval</span><b>Dense vs hybrid vs full pipeline →</b></Link><Link href="/architecture"><span>Inspectable workflow</span><b>See every LangGraph node →</b></Link></div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}

