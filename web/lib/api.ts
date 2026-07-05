import { getAuthHeaders, getUserId as getStoredUserId } from "./auth";

function resolveApiBaseUrl(): string {
  const configured = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  const isLocalhost =
    !configured ||
    configured.includes("localhost") ||
    configured.includes("127.0.0.1");

  // Production always uses same-origin API (Vercel Services rewrite → /api/v1)
  if (process.env.NODE_ENV === "production") {
    return isLocalhost ? "/api/v1" : configured;
  }

  return configured ?? "http://localhost:8000/api/v1";
}

export const API_BASE_URL = resolveApiBaseUrl();
export const DEFAULT_USER_ID =
  process.env.NEXT_PUBLIC_CREATOR_USER_ID ?? "demo-user";

export function getActiveUserId(): string {
  return getStoredUserId();
}

export type AuthTokenResponse = {
  access_token: string;
  token_type: string;
  expires_in_seconds: number;
  user_id: string;
};

export async function login(email: string, password: string): Promise<AuthTokenResponse> {
  return request<AuthTokenResponse>("/auth/token", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export type CreatorSettings = {
  notification_prefs: Record<string, boolean>;
  ai_provider: string;
  stripe_payout_status: "disconnected" | "connected" | "payouts_enabled";
};

export type CreatorProfile = {
  id: string;
  user_id: string;
  user: string;
  handle: string;
  niche: string | null;
  bio: string | null;
  target_platforms: string[];
  creator_voice: string | null;
  audience_size: number | null;
  settings?: CreatorSettings;
};

export type TrendReport = {
  id: string;
  user_id: string;
  title: string;
  summary: string | null;
  source: string | null;
  report_date: string | null;
};

export type ContentIdea = {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  status: string;
  score: number | null;
  created_at: string;
  updated_at: string;
};

export type CalendarItem = {
  id: string;
  user_id: string;
  content_idea_id: string | null;
  platform: string | null;
  scheduled_for: string | null;
  status: "idea" | "draft" | "scheduled" | "published";
  notes: string | null;
  created_at: string;
  updated_at: string;
};

export type CoachResponse = {
  direct_coaching_response: string;
  recommended_next_actions: string[];
  content_ideas: string[];
  risk_warning: string | null;
  agent_run_id: string | null;
  llm_provider?: string | null;
  llm_model?: string | null;
};

export type PlatformConnection = {
  platform: string;
  name: string;
  connected: boolean;
  configured: boolean;
  account_handle: string | null;
  account_name: string | null;
  connected_at: string | null;
};

export async function getPlatformConnections(): Promise<{ platforms: PlatformConnection[] }> {
  return request<{ platforms: PlatformConnection[] }>("/integrations/platforms");
}

export async function startPlatformConnection(platform: string): Promise<{
  authorization_url: string;
  platform: string;
}> {
  return request<{ authorization_url: string; platform: string }>(
    `/integrations/platforms/${encodeURIComponent(platform)}/connect`,
    { method: "POST" },
  );
}

export async function disconnectPlatform(platform: string): Promise<{ platform: string; disconnected: boolean }> {
  return request<{ platform: string; disconnected: boolean }>(
    `/integrations/platforms/${encodeURIComponent(platform)}`,
    { method: "DELETE" },
  );
}

export class ApiRequestError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
  }
}

async function request<T>(
  path: string,
  init?: RequestInit,
  options?: { timeoutMs?: number },
): Promise<T> {
  const timeoutMs = options?.timeoutMs ?? 0;
  const controller = timeoutMs > 0 ? new AbortController() : null;
  const timeoutId =
    controller && timeoutMs > 0
      ? globalThis.setTimeout(() => controller.abort(), timeoutMs)
      : null;

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      signal: controller?.signal,
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(),
        ...(init?.headers ?? {}),
      },
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error(
        "The coach is still thinking — Hermes can take up to 60 seconds on the first reply. Please try again and wait a bit longer.",
      );
    }
    throw new Error(
      `Cannot reach the API at ${API_BASE_URL}. Start it from api/ with: cd api && make dev`,
    );
  } finally {
    if (timeoutId !== null) {
      globalThis.clearTimeout(timeoutId);
    }
  }

  if (!response.ok) {
    const body = await response.text();
    let message = body;
    try {
      const parsed = JSON.parse(body) as {
        error?: { message?: string };
        detail?: string | Array<{ msg?: string }>;
      };
      if (Array.isArray(parsed.detail)) {
        message = parsed.detail.map((item) => item.msg).filter(Boolean).join("; ") || message;
      } else {
        message = parsed.error?.message ?? parsed.detail ?? body;
      }
    } catch {
      // keep raw body
    }
    throw new ApiRequestError(message || `API ${response.status}`, response.status);
  }

  return (await response.json()) as T;
}

export async function getProfile(): Promise<CreatorProfile | null> {
  try {
    return await request<CreatorProfile>("/creators/me");
  } catch {
    return null;
  }
}

export async function updateUser(user: string): Promise<CreatorProfile> {
  return request<CreatorProfile>("/creators/me/user", {
    method: "PATCH",
    body: JSON.stringify({ user }),
  });
}

export async function saveCreatorSettings(payload: {
  user?: string;
  notification_prefs?: Record<string, boolean>;
  ai_provider?: string;
  stripe_payout_status?: CreatorSettings["stripe_payout_status"];
}): Promise<CreatorProfile> {
  return request<CreatorProfile>("/creators/me/settings", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

/** @deprecated Use getProfile. Kept for compatibility — no longer creates fallback profiles. */
export async function getOrCreateProfile(): Promise<CreatorProfile> {
  const profile = await getProfile();
  if (!profile) {
    throw new Error("Creator profile not found. Re-run seed and sign in again.");
  }
  return profile;
}

export async function getTrends(limit = 10) {
  return request<{ trends: TrendReport[] }>(`/trends/latest?limit=${limit}`);
}

export async function runTrendResearch(payload: {
  creator_niche: string;
  target_platforms: string[];
  audience_description: string;
}) {
  return request<{ task_id: string; status: string }>("/trends/run-research", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getIdeas(limit = 50) {
  return request<{ ideas: ContentIdea[] }>(`/content-ideas?limit=${limit}`);
}

export async function generateIdea(payload: {
  topic: string;
  platform: string;
  creator_voice: string;
  goal: string;
  audience: string;
}) {
  return request<{
    title: string;
    description: string;
    suggested_score: number;
    status: string;
  }>("/content-ideas/generate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function saveIdea(payload: {
  title: string;
  description: string;
  trend_report_id?: string;
  score?: number;
  status?: string;
}) {
  return request<ContentIdea>("/content-ideas", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getCalendar(limit = 100) {
  return request<{ items: CalendarItem[] }>(`/calendar?limit=${limit}`);
}

export async function createCalendarItem(payload: {
  content_idea_id?: string;
  platform?: string;
  scheduled_for: string;
  status?: "idea" | "draft" | "scheduled" | "published";
  notes?: string;
}) {
  return request<CalendarItem>("/calendar", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateCalendarItemStatus(payload: {
  item_id: string;
  status: "idea" | "draft" | "scheduled" | "published";
}) {
  return request<CalendarItem>(`/calendar/${encodeURIComponent(payload.item_id)}/status`, {
    method: "PATCH",
    body: JSON.stringify({ status: payload.status }),
  });
}

export async function moveCalendarItemDate(payload: {
  item_id: string;
  scheduled_for: string;
}) {
  return request<CalendarItem>(`/calendar/${encodeURIComponent(payload.item_id)}/move-date`, {
    method: "PATCH",
    body: JSON.stringify({ scheduled_for: payload.scheduled_for }),
  });
}

export async function askCoach(payload: { question: string }): Promise<CoachResponse> {
  return request<CoachResponse>(
    "/coach/chat",
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
    { timeoutMs: 120_000 },
  );
}
