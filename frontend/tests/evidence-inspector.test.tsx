import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { EvidenceInspector } from "@/components/investigation/evidence-inspector";

describe("EvidenceInspector", () => {
  it("renders untrusted HTML-shaped content as text", () => {
    render(
      <EvidenceInspector evidence={{
        id: "issue-482",
        source_id: "checkout-incident",
        kind: "issue",
        title: "Untrusted issue",
        content: '<script>alert("unsafe")</script>',
        source_path: "issues/482.json",
        metadata: { service: "checkout-api" },
        content_hash: "abc",
        occurred_at: null,
      }} />,
    );

    expect(screen.getByText('<script>alert("unsafe")</script>')).toBeInTheDocument();
    expect(document.querySelector("script")).not.toBeInTheDocument();
    expect(screen.getByRole("link", { name: /open full source/i })).toHaveAttribute(
      "href",
      "/evidence/issue-482",
    );
  });
});

