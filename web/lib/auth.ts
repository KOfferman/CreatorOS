const TOKEN_KEY = "creatoros.access_token";
const USER_ID_KEY = "creatoros.user_id";
const EMAIL_KEY = "creatoros.email";

export type AuthSession = {
  accessToken: string;
  userId: string;
  email: string;
};

export function getSession(): AuthSession | null {
  if (typeof window === "undefined") return null;
  const accessToken = localStorage.getItem(TOKEN_KEY);
  const userId = localStorage.getItem(USER_ID_KEY);
  const email = localStorage.getItem(EMAIL_KEY);
  if (!accessToken || !userId) return null;
  return { accessToken, userId, email: email ?? "" };
}

export function setSession(session: AuthSession): void {
  localStorage.setItem(TOKEN_KEY, session.accessToken);
  localStorage.setItem(USER_ID_KEY, session.userId);
  localStorage.setItem(EMAIL_KEY, session.email);
}

export function clearSession(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_ID_KEY);
  localStorage.removeItem(EMAIL_KEY);
}

export function getAuthHeaders(): Record<string, string> {
  const session = getSession();
  if (!session) return {};
  return { Authorization: `Bearer ${session.accessToken}` };
}

export function getUserId(): string {
  return getSession()?.userId ?? process.env.NEXT_PUBLIC_CREATOR_USER_ID ?? "demo-user";
}
