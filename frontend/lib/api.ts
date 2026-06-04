import type {
  ChatRequest, ChatResponse, FundListItem,
  FundDetails, HealthResponse,
} from "./types";


class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30_000);
  try {
    const res = await fetch(`/api/proxy${path}`, {
      headers: { "Content-Type": "application/json" },
      signal: controller.signal,
      ...init,
    });
    if (!res.ok) {
      const body = await res.text().catch(() => "");
      throw new ApiError(res.status, body || res.statusText);
    }
    return res.json() as Promise<T>;
  } catch (err) {
    if ((err as Error).name === "AbortError") {
      throw new ApiError(408, "Request timed out. The backend may be slow — please try again.");
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
}

export async function fetchHealth(): Promise<HealthResponse> {
  return apiFetch<HealthResponse>("/health");
}

export async function fetchFunds(country?: string | null): Promise<FundListItem[]> {
  const qs = country ? `?country=${encodeURIComponent(country)}` : "";
  const all = await apiFetch<FundListItem[]>(`/funds${qs}`);
  return all.filter((f) => !f.is_backup);
}

export async function fetchFundDetails(fundId: string): Promise<FundDetails> {
  return apiFetch<FundDetails>(`/funds/${encodeURIComponent(fundId)}/details`);
}

export async function postChat(req: ChatRequest): Promise<ChatResponse> {
  return apiFetch<ChatResponse>("/chat", {
    method: "POST",
    body: JSON.stringify(req),
  });
}

export { ApiError };
