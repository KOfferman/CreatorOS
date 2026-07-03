const TOKEN_KEY = "creatoros.access_token";
const USER_ID_KEY = "creatoros.user_id";
const EMAIL_KEY = "creatoros.email";

export type AuthSession = {
  /** Bearer token — stored in localStorage only in cross-origin local dev. */
  accessToken?: string;
  userId: string;
  email: string;
};

/**
 * Production and same-origin deployments rely on the HttpOnly session cookie only.
 * Bearer-in-localStorage is enabled for local cross-origin dev (e.g. :3000 → :8000).
 */
export function usesDevTokenStorage(): boolean {
  if (process.env.NODE_ENV === "production") {
    return false;
  }
  const configured = process.env.NEXT_PUBLIC_API_BASE_URL?.trim() ?? "";
  if (!configured || configured.startsWith("/")) {
    return false;
  }
  return (
    configured.includes("localhost") ||
    configured.includes("127.0.0.1") ||
    process.env.NEXT_PUBLIC_DEV_TOKEN_STORAGE === "true"
  );
}

export function getSession(): AuthSession | null {
  if (typeof window === "undefined") return null;
  const userId = sessionStorage.getItem(USER_ID_KEY);
  const email = sessionStorage.getItem(EMAIL_KEY) ?? "";
  if (!userId) return null;
  const accessToken = usesDevTokenStorage()
    ? localStorage.getItem(TOKEN_KEY) ?? undefined
    : undefined;
  return { accessToken, userId, email };
}

export function setSession(session: AuthSession): void {
  sessionStorage.setItem(USER_ID_KEY, session.userId);
  sessionStorage.setItem(EMAIL_KEY, session.email);
  if (usesDevTokenStorage() && session.accessToken) {
    localStorage.setItem(TOKEN_KEY, session.accessToken);
  } else {
    localStorage.removeItem(TOKEN_KEY);
  }
}

export function clearSession(): void {
  localStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(USER_ID_KEY);
  sessionStorage.removeItem(EMAIL_KEY);
}

export function getAuthHeaders(): Record<string, string> {
  if (!usesDevTokenStorage()) {
    return {};
  }
  const token = localStorage.getItem(TOKEN_KEY);
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export function getUserId(): string {
  return getSession()?.userId ?? process.env.NEXT_PUBLIC_CREATOR_USER_ID ?? "demo-user";
}
