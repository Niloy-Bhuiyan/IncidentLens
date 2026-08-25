import type { Metadata } from "next";

import { InvestigationWorkspace } from "@/components/investigation/workspace";

export const metadata: Metadata = { title: "Checkout investigation" };

export default async function InvestigationPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <InvestigationWorkspace initialId={id} />;
}

