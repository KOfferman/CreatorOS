"use client";

import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { ChevronRight, Eye, RefreshCw, Search, Sparkles, Wand2 } from "lucide-react";

import {
  generateIdea,
  getProfile,
  getTrends,
  runTrendResearch,
  type TrendReport,
} from "../../lib/api";
import { IgIcon, TtIcon } from "../ui/platform-icons";

type PlatformFilter = "all" | "instagram" | "tiktok" | "youtube" | "multi" | "other";

type DerivedTrend = TrendReport & {
  platform: PlatformFilter;
  trendScore: number;
  confidenceScore: number;
  suggestedAngle: string;
  views: string;
  growth: string;
};

function normalizePlatform(source: string | null): PlatformFilter {
  const value = (source ?? "").toLowerCase();
  if (value.includes("instagram")) return "instagram";
  if (value.includes("tiktok")) return "tiktok";
  if (value.includes("youtube")) return "youtube";
  if (value.includes("multi") || value.includes("cross")) return "multi";
  return "other";
}

function seededScore(seed: string, min: number, max: number): number {
  const hash = seed.split("").reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return min + (hash % (max - min + 1));
}

function buildSuggestedAngle(summary: string | null, title: string): string {
  if (summary) {
    const sentence = summary.split(".").map((part) => part.trim()).find(Boolean);
    if (sentence) return sentence;
  }
  return `Share a quick creator take on "${title}" with one actionable tip.`;
}

export function TrendsScreen() {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [searching, setSearching] = useState(false);
  const [loading, setLoading] = useState(false);
  const [generatingId, setGeneratingId] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [activeModel, setActiveModel] = useState("claude");
  const [platformFilter, setPlatformFilter] = useState<PlatformFilter>("all");
  const [trends, setTrends] = useState<TrendReport[]>([]);
  const [profileNiche, setProfileNiche] = useState("Lifestyle & self-growth");

  const loadTrends = async () => {
    setLoading(true);
    try {
      const [profile, result] = await Promise.all([
        getProfile().catch(() => null),
        getTrends(20),
      ]);
      if (profile?.niche) setProfileNiche(profile.niche);
      setTrends(result.trends);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadTrends();
  }, []);

  const derivedTrends = useMemo<DerivedTrend[]>(
    () =>
      trends.map((trend) => ({
        ...trend,
        platform: normalizePlatform(trend.source),
        trendScore: seededScore(trend.id, 78, 98),
        confidenceScore: seededScore(`${trend.id}-conf`, 62, 94),
        suggestedAngle: buildSuggestedAngle(trend.summary, trend.title),
        views: `${(seededScore(trend.id, 3, 12) / 10).toFixed(1)}M`,
        growth: `+${seededScore(`${trend.id}-g`, 80, 340)}%`,
      })),
    [trends],
  );

  const filtered = derivedTrends.filter(
    (trend) => platformFilter === "all" || trend.platform === platformFilter,
  );

  const handleSearch = async () => {
    if (!query.trim()) return;
    setSearching(true);
    try {
      await runTrendResearch({
        creator_niche: profileNiche,
        target_platforms: ["instagram", "tiktok", "youtube"],
        audience_description: query,
      });
      await loadTrends();
    } finally {
      setSearching(false);
    }
  };

  const handleGenerate = async (trend: DerivedTrend) => {
    setGeneratingId(trend.id);
    try {
      await generateIdea({
        topic: trend.title,
        platform: trend.platform === "tiktok" ? "tiktok" : "instagram",
        creator_voice: "warm, honest, reflective, practical",
        goal: "engagement",
        audience: profileNiche,
      });
      router.push(`/generator?topic=${encodeURIComponent(trend.title)}`);
    } finally {
      setGeneratingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="mb-1 text-[1.65rem] font-extrabold text-white">Trend Research Agent</h1>
        <p className="text-sm text-[#717182]">AI-powered trend discovery across all platforms</p>
      </div>

      <div className="flex flex-wrap items-center gap-3 rounded-xl border border-white/5 bg-[#0F0F1C] px-4 py-3">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 animate-pulse rounded-full bg-emerald-400" />
          <span className="text-xs text-[#717182]">AI Provider</span>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {[
            { id: "claude", label: "Claude 3.5" },
            { id: "gpt4o", label: "GPT-4o" },
            { id: "gemini", label: "Gemini 1.5" },
          ].map((m) => (
            <button
              key={m.id}
              type="button"
              onClick={() => setActiveModel(m.id)}
              className={`rounded-full px-2.5 py-1 text-xs font-medium transition-all ${
                activeModel === m.id ? "bg-violet-600 text-white" : "bg-white/5 text-[#717182] hover:text-white"
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>
        <span className="ml-auto text-[10px] font-semibold uppercase tracking-wider text-emerald-400">
          Abstraction Active
        </span>
      </div>

      <div className="flex gap-3">
        <div className="relative flex-1">
          <Search size={14} className="absolute left-4 top-1/2 -translate-y-1/2 text-[#717182]" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && void handleSearch()}
            placeholder="Search topics, niches, formats..."
            className="w-full rounded-xl border border-white/8 bg-[#0F0F1C] py-3 pl-10 pr-4 text-sm text-white transition-all placeholder:text-[#717182] focus:border-violet-500/50 focus:outline-none focus:ring-1 focus:ring-violet-500/25"
          />
        </div>
        <button
          type="button"
          onClick={() => void handleSearch()}
          disabled={searching}
          className="flex flex-shrink-0 items-center gap-2 rounded-xl bg-violet-600 px-5 text-sm font-medium text-white transition-all hover:bg-violet-500 disabled:opacity-60"
        >
          {searching ? <RefreshCw size={14} className="animate-spin" /> : <Sparkles size={14} />}
          Analyze
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
        {(["all", "instagram", "tiktok", "youtube"] as PlatformFilter[]).map((p) => (
          <button
            key={p}
            type="button"
            onClick={() => setPlatformFilter(p)}
            className={`rounded-full px-3 py-1.5 text-xs font-medium capitalize transition-all ${
              platformFilter === p ? "bg-violet-600 text-white" : "bg-white/5 text-[#717182] hover:text-white"
            }`}
          >
            {p}
          </button>
        ))}
      </div>

      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-sm font-bold text-white">
            {query.trim() ? `Results for "${query}"` : "Trending in your niche"}
          </h2>
          <span className="text-xs text-[#717182]">{loading ? "Loading..." : "Updated just now"}</span>
        </div>
        <div className="space-y-3">
          {filtered.map((topic) => (
            <div
              key={topic.id}
              className="overflow-hidden rounded-2xl border border-white/5 bg-[#0F0F1C] transition-all hover:border-violet-500/15"
            >
              <div
                onClick={() => setExpanded(expanded === topic.id ? null : topic.id)}
                className="flex cursor-pointer items-start gap-4 p-5"
              >
                <div className="flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl border border-violet-500/15 bg-violet-500/10">
                  <span className="text-base font-bold text-violet-300" style={{ fontFamily: "'JetBrains Mono', monospace" }}>
                    {topic.trendScore}
                  </span>
                </div>
                <div className="min-w-0 flex-1">
                  <div className="mb-1.5 flex items-center gap-1.5">
                    {topic.platform === "instagram" && <IgIcon size={13} />}
                    {topic.platform === "tiktok" && <TtIcon size={13} />}
                    <span className="text-[11px] capitalize text-[#717182]">{topic.platform}</span>
                  </div>
                  <p className="mb-1.5 text-sm font-semibold text-white">{topic.title}</p>
                  <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1 text-xs text-[#717182]">
                      <Eye size={10} />
                      {topic.views}
                    </span>
                    <span className="text-xs font-semibold text-emerald-400">{topic.growth}</span>
                    <span className="text-xs text-[#717182]">Confidence {topic.confidenceScore}%</span>
                  </div>
                </div>
                <ChevronRight
                  size={15}
                  className={`flex-shrink-0 text-[#717182] transition-transform duration-200 ${
                    expanded === topic.id ? "rotate-90" : ""
                  }`}
                />
              </div>
              {expanded === topic.id ? (
                <div className="border-t border-white/5 px-5 pb-5 pt-4">
                  <p className="mb-3 text-[10px] font-bold uppercase tracking-widest text-[#717182]">
                    AI-suggested angle
                  </p>
                  <div className="flex items-center justify-between rounded-xl bg-white/3 px-4 py-2.5 transition-all hover:bg-white/5">
                    <span className="text-sm text-white/80">{topic.suggestedAngle}</span>
                    <button
                      type="button"
                      onClick={() => void handleGenerate(topic)}
                      disabled={generatingId === topic.id}
                      className="ml-4 flex flex-shrink-0 items-center gap-1.5 text-violet-400 transition-colors hover:text-violet-300"
                    >
                      {generatingId === topic.id ? (
                        <RefreshCw size={13} className="animate-spin" />
                      ) : (
                        <Wand2 size={13} />
                      )}
                      Generate
                    </button>
                  </div>
                </div>
              ) : null}
            </div>
          ))}
          {!filtered.length && !loading ? (
            <p className="text-sm text-[#717182]">No trends yet. Run Analyze to discover opportunities.</p>
          ) : null}
        </div>
      </div>
    </div>
  );
}
