"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  BarChart2,
  Bell,
  Bot,
  CalendarDays,
  FileText,
  Home,
  Lightbulb,
  LogOut,
  Menu,
  Mic,
  Settings,
  Sparkles,
  Wand2,
  X,
} from "lucide-react";
import type { ReactNode } from "react";
import { useState } from "react";

import { clearSession, getSession } from "../../lib/auth";

const NAV_ITEMS = [
  { href: "/", label: "Home", icon: Home },
  { href: "/posts", label: "Posts", icon: FileText },
  { href: "/insights", label: "Insights", icon: BarChart2 },
  { href: "/trends", label: "AI Ideas", icon: Lightbulb },
  { href: "/generator", label: "Generator", icon: Wand2 },
  { href: "/coach", label: "AI Coach", icon: Bot },
  { href: "/calendar", label: "Calendar", icon: CalendarDays },
  { href: "/profile", label: "My Voice", icon: Mic },
];

function isActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname.startsWith(href);
}

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const session = getSession();
  const displayName = session?.email?.split("@")[0] ?? "Creator";

  const handleLogout = () => {
    clearSession();
    router.replace("/login");
  };

  return (
    <div
      className="flex h-screen overflow-hidden bg-[#08080F]"
      style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}
    >
      {sidebarOpen ? (
        <div className="fixed inset-0 z-20 bg-black/60 lg:hidden" onClick={() => setSidebarOpen(false)} />
      ) : null}

      <aside
        className={`fixed left-0 top-0 z-30 flex h-full w-[220px] flex-col border-r border-white/5 bg-[#0C0C1A] transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0 lg:flex-shrink-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center gap-3 px-5 pb-7 pt-5">
          <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-xl bg-violet-600 shadow-md shadow-violet-900/50">
            <Sparkles size={14} className="text-white" />
          </div>
          <span className="text-sm font-bold tracking-tight text-white">CreatorOS</span>
          <button
            type="button"
            className="ml-auto text-[#717182] transition-colors hover:text-white lg:hidden"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={16} />
          </button>
        </div>

        <nav className="scrollbar-hide flex-1 space-y-0.5 overflow-y-auto px-3">
          {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
            const active = isActive(pathname, href);
            return (
              <Link
                key={href}
                href={href}
                onClick={() => setSidebarOpen(false)}
                className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all ${
                  active
                    ? "border border-violet-500/20 bg-violet-600/15 text-violet-300"
                    : "text-[#717182] hover:bg-white/5 hover:text-white"
                }`}
              >
                <Icon size={15} className="flex-shrink-0" />
                <span className="truncate">{label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="space-y-1 border-t border-white/5 p-4 pt-3">
          <Link
            href="/settings"
            onClick={() => setSidebarOpen(false)}
            className={`flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition-all ${
              pathname.startsWith("/settings")
                ? "bg-violet-600/10 text-violet-300"
                : "text-[#717182] hover:bg-white/5 hover:text-white"
            }`}
          >
            <Settings size={15} />
            <span>Settings</span>
          </Link>
          <div className="mt-1 flex items-center gap-3 px-3 py-2">
            <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-pink-500 text-xs font-bold uppercase text-white">
              {displayName.charAt(0)}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-semibold capitalize text-white">{displayName}</p>
              <p className="text-[10px] text-[#717182]">Pro Plan</p>
            </div>
            <button
              type="button"
              onClick={handleLogout}
              className="text-[#717182] transition-colors hover:text-red-400"
            >
              <LogOut size={13} />
            </button>
          </div>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">
        <header className="flex flex-shrink-0 items-center gap-4 border-b border-white/5 bg-[#08080F] px-5 py-3.5">
          <button
            type="button"
            onClick={() => setSidebarOpen(true)}
            className="p-1 text-[#717182] transition-colors hover:text-white lg:hidden"
          >
            <Menu size={19} />
          </button>
          <div className="flex-1" />
          <button type="button" className="relative p-1 text-[#717182] transition-colors hover:text-white">
            <Bell size={17} />
            <span className="absolute right-1 top-1 h-1.5 w-1.5 rounded-full bg-violet-500" />
          </button>
          <Link
            href="/profile"
            className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-pink-500 text-xs font-bold uppercase text-white transition-all hover:ring-2 hover:ring-violet-500/40"
          >
            {displayName.charAt(0)}
          </Link>
        </header>

        <main className="scrollbar-hide flex-1 overflow-y-auto p-5 lg:p-7">{children}</main>

        <nav className="flex flex-shrink-0 border-t border-white/5 bg-[#0C0C1A] lg:hidden">
          {NAV_ITEMS.slice(0, 5).map(({ href, label, icon: Icon }) => {
            const active = isActive(pathname, href);
            return (
              <Link
                key={href}
                href={href}
                className={`flex flex-1 flex-col items-center gap-0.5 py-2.5 text-xs transition-all ${
                  active ? "text-violet-400" : "text-[#717182]"
                }`}
              >
                <Icon size={17} />
                <span className="text-[9px] font-medium">{label}</span>
              </Link>
            );
          })}
        </nav>
      </div>
    </div>
  );
}
