import type { ReactNode } from "react";

export function PageTitle({
  title,
  subtitle,
  actions,
}: {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
      <div>
        <h1 className="text-2xl font-bold text-white">{title}</h1>
        {subtitle ? <p className="text-sm text-[#717182]">{subtitle}</p> : null}
      </div>
      {actions}
    </div>
  );
}
