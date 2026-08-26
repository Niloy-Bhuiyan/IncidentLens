import type { DemoSummary, EvaluationResult, Evidence, Investigation } from "./types";

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");
const REQUEST_TIMEOUT_MS = 25_000;

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly requestId?: string,
    public readonly status?: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeout = globalThis.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: { "Content-Type": "application/json", ...options?.headers },
      cache: "no-store",
      signal: controller.signal,
    });
  } catch (error) {
    if (typeof error === "object" && error !== null && "name" in error && error.name === "AbortError") {
      throw new ApiError("The investigation timed out. Please try the demo again.", "request_timeout");
    }
    throw new ApiError("The investigation API could not be reached. Please try again.", "network_error");
  } finally {
    globalThis.clearTimeout(timeout);
  }
  let payload: unknown;
  try {
    payload = await response.json();
  } catch {
    throw new ApiError(
      response.ok ? "The investigation API returned an invalid response." : `Request failed with status ${response.status}`,
      "invalid_response",
      undefined,
      response.status,
    );
  }
  if (!response.ok) {
    const error =
      typeof payload === "object" && payload !== null && "error" in payload
        ? (payload as { error?: { code?: string; message?: string; request_id?: string } }).error
        : undefined;
    throw new ApiError(
      error?.message || `Request failed with status ${response.status}`,
      error?.code || "request_failed",
      error?.request_id,
      response.status,
    );
  }
  return payload as T;
}

export const api = {
  demo: () => request<DemoSummary>("/api/v1/demo"),
  investigate: (question: string, forceCorrective = false) =>
    request<Investigation>("/api/v1/investigations", {
      method: "POST",
      body: JSON.stringify({ question, provider: "mock", force_corrective: forceCorrective }),
    }),
  investigation: (id: string) => request<Investigation>(`/api/v1/investigations/${encodeURIComponent(id)}`),
  evidence: (id: string) =>
    request<{ evidence: Evidence; relations: Array<Record<string, unknown>> }>(
      `/api/v1/evidence/${encodeURIComponent(id)}`,
    ),
  evaluation: () => request<EvaluationResult>("/api/v1/evaluation/latest"),
};
