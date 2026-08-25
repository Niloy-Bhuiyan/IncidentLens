import Link from "next/link";

export default function NotFound() {
  return <main className="notFound"><span className="eyebrow">404 · no evidence here</span><h1>This trail ends here.</h1><p>The route does not map to an incident or evidence source.</p><Link className="primaryButton" href="/">Return to IncidentLens →</Link></main>;
}

