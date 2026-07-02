import type { ReactNode } from "react";

export function Panel({ children }: { children: ReactNode }) {
  return <section className="rounded-2xl border border-white/10 bg-[#0F0F1C] p-4">{children}</section>;
}
