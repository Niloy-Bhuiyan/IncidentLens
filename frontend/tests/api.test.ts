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
        signal: expect.any(AbortSignal),
        body: JSON.stringify({
          question: "Why did checkout fail?",
          provider: "mock",
          force_corrective: true,
        }),
      }),
    );
  });

  it("translates network failures without exposing internals", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("connection details")));

    await expect(api.investigate("Why did checkout fail?")).rejects.toEqual(
      expect.objectContaining({ code: "network_error" }),
    );
    await expect(api.investigate("Why did checkout fail?")).rejects.toThrow(/could not be reached/i);
  });

  it("aborts a stalled investigation instead of loading forever", async () => {
    vi.useFakeTimers();
    vi.stubGlobal("fetch", vi.fn().mockImplementation((_url: string, options: RequestInit) => (
      new Promise((_resolve, reject) => {
        options.signal?.addEventListener("abort", () => reject(new DOMException("aborted", "AbortError")));
      })
    )));

    const request = api.investigate("Why did checkout fail?");
    const expectation = expect(request).rejects.toEqual(expect.objectContaining({ code: "request_timeout" }));
    await vi.advanceTimersByTimeAsync(25_001);
    await expectation;
    vi.useRealTimers();
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
