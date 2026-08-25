import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="siteFooter">
      <p>Evidence first. Conclusions second.</p>
      <div>
        <Link href="/architecture">System design</Link>
        <Link href="/evaluation">Measured retrieval</Link>
      </div>
    </footer>
  );
}

