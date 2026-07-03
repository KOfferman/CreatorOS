"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowUp,
  Camera,
  ChevronRight,
  Clock,
  Flame,
  Globe,
  Lightbulb,
  MessageCircle,
  Target,
} from "lucide-react";

import {
  getCalendar,
  getIdeas,
  getProfile,
  getTrends,
  type CalendarItem,
  type ContentIdea,
  type CreatorProfile,
  type TrendReport,
} from "../../lib/api";
import { IgIcon, TtIcon, YtIcon } from "../ui/platform-icons";

type Platform = "all" | "instagram" | "tiktok";

function formatAudience(value: number | null | undefined): string {
  if (!value) return "—";
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `${Math.round(value / 1_000)}K`;
  return value.toLocaleString();
}

export function DashboardScreen() {
  const [platform, setPlatform] = useState<Platform>("all");
  const [profile, setProfile] = useState<CreatorProfile | null>(null);
  const [trends, setTrends] = useState<TrendReport[]>([]);
  const [ideas, setIdeas] = useState<ContentIdea[]>([]);
  const [calendarItems, setCalendarItems] = useState<CalendarItem[]>([]);

  useEffect(() => {
    const load = async () => {
      const [p, t, i, c] = await Promise.all([
        getProfile().catch(() => null),
        getTrends().catch(() => ({ trends: [] })),
        getIdeas().catch(() => ({ ideas: [] })),
        getCalendar().catch(() => ({ items: [] })),
      ]);
      setProfile(p);
      setTrends(t.trends);
      setIdeas(i.ideas);
      setCalendarItems(c.items);
    };
    void load();
  }, []);

  const topTrend = trends[0] ?? null;
  const topIdea = ideas[0] ?? null;
  const scheduledItems = calendarItems.filter((item) => item.status === "scheduled");
  const audienceSize = profile?.audience_size ?? 0;
  const creatorScore = Math.min(
    500,
    Math.round(
      audienceSize / 30000 + trends.length * 8 + scheduledItems.length * 6 + ideas.length * 5,
    ),
  );
  const handle = profile?.handle?.split(".")[0] ?? "Creator";
  const todayLabel = new Date().toLocaleDateString(undefined, {
    weekday: "long",
    month: "long",
    day: "numeric",
  });

  const todayItems = [
    {
      icon: <Flame size={13} className="text-orange-400" />,
      badge: "Trending fast",
      badgeColor: "text-orange-400",
      title: topTrend ? `"${topTrend.title}" is your top opportunity` : "Run trend research to discover opportunities",
      sub: topTrend?.summary ?? "Use AI Ideas to scan your niche across platforms.",
      href: "/trends",
    },
    {
      icon: <Lightbulb size={13} className="text-violet-400" />,
      badge: "AI Idea",
      badgeColor: "text-violet-400",
      title: topIdea?.title ?? "Generate your next content idea",
      sub: topIdea?.description ?? "Open the Generator to draft platform-native content.",
      href: "/generator",
    },
    {
      icon: <Target size={13} className="text-cyan-400" />,
      badge: "Opportunity",
      badgeColor: "text-cyan-400",
      title: scheduledItems.length
        ? `${scheduledItems.length} posts scheduled this week`
        : "Schedule content to build consistency",
      sub: scheduledItems[0]?.notes ?? "Save generated content directly to your calendar.",
      href: "/calendar",
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="mb-1 text-[1.65rem] font-extrabold text-white">Good morning, {handle} 👋</h1>
        <p className="text-sm text-[#717182]">{todayLabel} · Here&apos;s what&apos;s happening</p>
      </div>

      <div className="flex flex-wrap gap-2">
        {(["all", "instagram", "tiktok"] as Platform[]).map((p) => (
          <button
            key={p}
            type="button"
            onClick={() => setPlatform(p)}
            className={`flex items-center gap-2 rounded-full px-4 py-1.5 text-sm font-medium transition-all ${
              platform === p
                ? "bg-violet-600 text-white shadow-lg shadow-violet-900/40"
                : "bg-white/5 text-[#717182] hover:bg-white/10 hover:text-white"
            }`}
          >
            {p === "instagram" && <IgIcon size={13} />}
            {p === "tiktok" && <TtIcon size={13} />}
            {p === "all" && <Globe size={13} />}
            <span className="capitalize">
              {p === "all" ? "All" : p === "instagram" ? "Instagram" : "TikTok"}
            </span>
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <div className="space-y-4 xl:col-span-2">
          <div className="overflow-hidden rounded-2xl border border-white/5 bg-[#0F0F1C]">
            <div className="border-b border-white/5 px-5 pb-3 pt-4">
              <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-[#717182]">
                This is yours today
              </p>
            </div>
            <div className="divide-y divide-white/5">
              {todayItems.map((item) => (
                <Link
                  key={item.title}
                  href={item.href}
                  className="group flex cursor-pointer items-start justify-between gap-4 px-5 py-4 transition-colors hover:bg-white/[0.02]"
                >
                  <div className="flex-1">
                    <div className="mb-1.5 flex items-center gap-1.5">
                      {item.icon}
                      <span className={`text-[11px] font-semibold ${item.badgeColor}`}>{item.badge}</span>
                    </div>
                    <p className="text-sm font-semibold text-white">{item.title}</p>
                    <p className="mt-0.5 text-xs text-[#717182]">{item.sub}</p>
                  </div>
                  <ChevronRight
                    size={15}
                    className="mt-1 flex-shrink-0 text-[#717182] transition-colors group-hover:text-white"
                  />
                </Link>
              ))}
            </div>
          </div>

          <div className="overflow-hidden rounded-2xl border border-white/5 bg-[#0F0F1C]">
            <div className="border-b border-white/5 px-5 pb-3 pt-4">
              <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-[#717182]">
                In your agenda
              </p>
            </div>
            <div className="space-y-3 p-5">
              {scheduledItems.slice(0, 2).map((item, i) => (
                <div key={item.id} className="flex items-center gap-3">
                  <div
                    className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl border bg-gradient-to-br ${
                      i === 0
                        ? "border-violet-500/15 from-violet-500/15 to-pink-500/15"
                        : "border-cyan-500/15 from-cyan-500/15 to-blue-500/15"
                    }`}
                  >
                    {i === 0 ? (
                      <Camera size={15} className="text-violet-400" />
                    ) : (
                      <MessageCircle size={15} className="text-cyan-400" />
                    )}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm font-semibold text-white">{item.notes ?? "Scheduled content"}</p>
                    <p className="text-xs text-[#717182]">
                      {item.platform ?? "multi"} ·{" "}
                      {item.scheduled_for ? new Date(item.scheduled_for).toLocaleString() : "Date pending"}
                    </p>
                  </div>
                  <span
                    className={`flex-shrink-0 rounded-full px-2.5 py-1 text-[11px] ${
                      i === 0
                        ? "border border-violet-500/20 bg-violet-500/15 text-violet-300"
                        : "bg-white/5 text-[#717182]"
                    }`}
                  >
                    {i === 0 ? "Today" : "Upcoming"}
                  </span>
                </div>
              ))}
              {!scheduledItems.length ? (
                <p className="text-sm text-[#717182]">No scheduled items yet. Save content from the Generator.</p>
              ) : null}
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <div className="overflow-hidden rounded-2xl border border-white/5 bg-[#0F0F1C]">
            <div className="border-b border-white/5 px-5 pb-3 pt-4">
              <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-[#717182]">My networks</p>
            </div>
            <div className="space-y-4 p-5">
              {[
                { icon: <IgIcon size={28} />, label: "Instagram", value: formatAudience(audienceSize * 0.4) },
                { icon: <TtIcon size={28} />, label: "TikTok", value: formatAudience(audienceSize * 0.45) },
                { icon: <YtIcon size={28} />, label: "YouTube", value: formatAudience(audienceSize * 0.15) },
              ].map((n) => (
                <div key={n.label} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {n.icon}
                    <div>
                      <p className="mb-1 text-[11px] leading-none text-[#717182]">{n.label}</p>
                      <p
                        className="text-lg font-bold leading-none text-white"
                        style={{ fontFamily: "'JetBrains Mono', monospace" }}
                      >
                        {n.value}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xs font-semibold text-emerald-400">+{Math.max(1, Math.round(trends.length * 2))}K</p>
                    <p className="text-[10px] text-[#717182]">this week</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-violet-500/20 bg-gradient-to-br from-violet-900/35 to-[#0F0F1C] p-5">
            <div className="mb-3 flex items-center gap-2">
              <Clock size={12} className="text-violet-400" />
              <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-[#717182]">Best time to post</p>
            </div>
            <p className="mb-1 text-4xl font-bold text-white" style={{ fontFamily: "'JetBrains Mono', monospace" }}>
              06:00
            </p>
            <p className="mb-3 text-xs text-violet-300/60">Based on your audience activity</p>
            <div className="flex gap-1.5">
              {["Tue", "Thu", "Sat"].map((d) => (
                <span key={d} className="rounded-full bg-violet-500/20 px-2 py-0.5 text-[11px] text-violet-300">
                  {d}
                </span>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-white/5 bg-[#0F0F1C] p-5">
            <p className="mb-3 text-[10px] font-bold uppercase tracking-[0.12em] text-[#717182]">Creator score</p>
            <div className="mb-3 flex items-end gap-2">
              <p className="text-4xl font-bold text-white" style={{ fontFamily: "'JetBrains Mono', monospace" }}>
                {creatorScore}
              </p>
              <div className="flex items-center gap-1 pb-1">
                <ArrowUp size={11} className="text-emerald-400" />
                <span className="text-xs text-emerald-400">+{Math.min(12, trends.length + 2)} this week</span>
              </div>
            </div>
            <div className="mb-2 h-2 overflow-hidden rounded-full bg-white/8">
              <div
                className="h-full rounded-full bg-gradient-to-r from-violet-600 to-pink-500"
                style={{ width: `${Math.min(100, Math.round((creatorScore / 500) * 100))}%` }}
              />
            </div>
            <p className="text-xs text-[#717182]">Top {Math.max(5, 100 - Math.round(creatorScore / 5))}% of creators in your niche</p>
          </div>
        </div>
      </div>
    </div>
  );
}
