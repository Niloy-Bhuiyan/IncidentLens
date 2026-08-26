import Image from "next/image";
import Link from "next/link";

const links = [
  ["Investigate", "/investigations/demo"],
  ["Evaluation", "/evaluation"],
  ["Under the Hood", "/under-the-hood"],
  ["About", "/about"],
];

export function SiteHeader() {
  return (
    <header className="siteHeader">
      <div className="navShell">
        <Link className="brand" href="/" aria-label="IncidentLens home">
          <Image src="/images/mark.svg" alt="" width={34} height={34} priority />
          <span>IncidentLens</span>
        </Link>
        <nav aria-label="Primary navigation">
          {links.map(([label, href]) => (
            <Link key={href} href={href}>
              {label}
            </Link>
          ))}
        </nav>
        <span className="demoStatus"><i aria-hidden="true" /> Deterministic demo</span>
      </div>
    </header>
  );
}

