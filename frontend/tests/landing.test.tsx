import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { LandingDemo } from "@/components/landing-demo";

describe("LandingDemo", () => {
  it("offers the real demo route and describes the pipeline", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        id: "checkout-incident",
        title: "Checkout evidence",
        suggested_question: "Why did checkout failures increase?",
        source_count: 10,
        chunk_count: 11,
        relationship_count: 10,
        source_types: {},
        occurred_at: "2026-08-19T10:14:00Z",
      }),
    }));

    render(<LandingDemo />);

    expect(screen.getByRole("link", { name: /investigate this incident/i })).toHaveAttribute(
      "href",
      "/investigations/demo",
    );
    expect(screen.getByText(/vector \+ BM25 retrieval/i)).toBeInTheDocument();
    expect(await screen.findByText(/Checkout evidence/)).toBeInTheDocument();
  });
});
