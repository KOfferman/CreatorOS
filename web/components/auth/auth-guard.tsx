"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";

import { API_BASE_URL } from "../../lib/api";
import { clearSession, getAuthHeaders, getSession } from "../../lib/auth";

export function AuthGuard({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const session = getSession();
    if (!session) {
      router.replace("/login");
      return;
    }

    const validate = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/creators/me`, {
          credentials: "include",
          headers: getAuthHeaders(),
        });
        if (!response.ok) {
          clearSession();
          router.replace("/login");
          return;
        }
        setReady(true);
      } catch {
        clearSession();
        router.replace("/login");
      }
    };

    void validate();
  }, [router]);

  if (!ready) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#08080F] text-[#717182]">
        Loading...
      </div>
    );
  }

  return <>{children}</>;
}
