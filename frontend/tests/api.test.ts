import { describe, expect, it, vi } from "vitest";

import { api } from "@/lib/api";

describe("API client", () => {
  it("posts a typed mock investigation request", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, json: async () => ({ id: "inv-1" }) });
    vi.stubGlobal("fetch", fetchMock);

    await api.investigate("Why did checkout fail?", true);

    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/investigations",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          question: "Why did checkout fail?",
          provider: "mock",
          force_corrective: true,
        }),
      }),
    );
  });

  it("preserves safe request metadata on errors", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: false,
      status: 503,
      json: async () => ({
        error: { code: "provider_unavailable", message: "Provider failed", request_id: "request-123" },
      }),
    }));

    await expect(api.investigate("Why did checkout fail?")).rejects.toEqual(
      expect.objectContaining({
        name: "ApiError",
        message: "Provider failed",
        code: "provider_unavailable",
        requestId: "request-123",
        status: 503,
      }),
    );
  });
});
