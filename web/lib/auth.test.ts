import { afterEach, describe, expect, it, vi } from "vitest";

import { clearSession, getAuthHeaders, setSession, usesDevTokenStorage } from "./auth";

describe("usesDevTokenStorage", () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it("is false in production", () => {
    vi.stubEnv("NODE_ENV", "production");
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://localhost:8000/api/v1");
    expect(usesDevTokenStorage()).toBe(false);
  });

  it("is false for same-origin relative API", () => {
    vi.stubEnv("NODE_ENV", "development");
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "/api/v1");
    expect(usesDevTokenStorage()).toBe(false);
  });

  it("is true for cross-origin local API", () => {
    vi.stubEnv("NODE_ENV", "development");
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://localhost:8000/api/v1");
    expect(usesDevTokenStorage()).toBe(true);
  });
});

describe("session storage", () => {
  afterEach(() => {
    clearSession();
    vi.unstubAllEnvs();
  });

  it("does not persist bearer token when same-origin", () => {
    vi.stubEnv("NODE_ENV", "development");
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "/api/v1");
    setSession({ accessToken: "secret-token", userId: "u1", email: "a@b.com" });
    expect(localStorage.getItem("creatoros.access_token")).toBeNull();
    expect(getAuthHeaders()).toEqual({});
    expect(sessionStorage.getItem("creatoros.user_id")).toBe("u1");
  });

  it("persists bearer token for cross-origin local dev", () => {
    vi.stubEnv("NODE_ENV", "development");
    vi.stubEnv("NEXT_PUBLIC_API_BASE_URL", "http://localhost:8000/api/v1");
    setSession({ accessToken: "dev-token", userId: "u1", email: "a@b.com" });
    expect(localStorage.getItem("creatoros.access_token")).toBe("dev-token");
    expect(getAuthHeaders()).toEqual({ Authorization: "Bearer dev-token" });
  });
});
