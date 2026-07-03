"use client";

import { useEffect, useState } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ArrowUp } from "lucide-react";

import { getIdeas, getProfile, getTrends } from "../../lib/api";

const FOLLOWER_DATA = [
  { month: "Jan", ig: 1600, tt: 1900, yt: 380 },
  { month: "Feb", ig: 1650, tt: 2000, yt: 395 },
  { month: "Mar", ig: 1720, tt: 2080, yt: 410 },
  { month: "Apr", ig: 1780, tt: 2150, yt: 425 },
  { month: "May", ig: 1840, tt: 2220, yt: 438 },
  { month: "Jun", ig: 1900, tt: 2300, yt: 450 },
];

const ENGAGEMENT_DATA = [
  { day: "Mon", rate: 4.2 },
  { day: "Tue", rate: 5.8 },
  { day: "Wed", rate: 3.9 },
  { day: "Thu", rate: 6.4 },
  { day: "Fri", rate: 7.2 },
  { day: "Sat", rate: 8.5 },
  { day: "Sun", rate: 6.1 },
];

export function InsightsScreen() {
  const [audienceSize, setAudienceSize] = useState(0);
  const [ideasCount, setIdeasCount] = useState(0);
  const [trendsCount, setTrendsCount] = useState(0);

  useEffect(() => {
    void Promise.all([getProfile(), getIdeas(), getTrends()]).then(([profile, ideas, trends]) => {
      setAudienceSize(profile?.audience_size ?? 0);
      setIdeasCount(ideas.ideas.length);
      setTrendsCount(trends.trends.length);
    }).catch(() => undefined);
  }, []);

  const avgScore =
    ideasCount > 0 ? `${Math.min(9.9, 4 + ideasCount * 0.2 + trendsCount * 0.15).toFixed(1)}%` : "6.3%";

  return (
    <div className="space-y-6">
      <div>
        <h1 className="mb-1 text-[1.65rem] font-extrabold text-white">Audience Insights</h1>
        <p className="text-sm text-[#717182]">Combined across Instagram, TikTok & YouTube</p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          { label: "Total Followers", value: audienceSize ? `${(audienceSize / 1_000_000).toFixed(2)}M` : "4.65M", change: "+58K", up: true },
          { label: "Avg. Engagement", value: avgScore, change: "+0.4%", up: true },
          { label: "Content Ideas", value: String(ideasCount), change: `+${Math.max(1, trendsCount)}`, up: true },
          { label: "Trend Reports", value: String(trendsCount), change: "+2", up: true },
        ].map((s) => (
          <div key={s.label} className="rounded-2xl border border-white/5 bg-[#0F0F1C] p-5">
            <p className="mb-2 text-xs text-[#717182]">{s.label}</p>
            <p className="mb-1.5 text-2xl font-bold text-white" style={{ fontFamily: "'JetBrains Mono', monospace" }}>
              {s.value}
            </p>
            <div className={`flex items-center gap-1 text-xs font-semibold ${s.up ? "text-emerald-400" : "text-red-400"}`}>
              <ArrowUp size={10} className={s.up ? "" : "rotate-180"} />
              {s.change}
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-2xl border border-white/5 bg-[#0F0F1C] p-5">
          <h3 className="mb-4 text-sm font-bold text-white">Follower Growth (K)</h3>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={FOLLOWER_DATA} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="gIg" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#E1306C" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="#E1306C" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gTt" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#06B6D4" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="#06B6D4" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="month" tick={{ fill: "#717182", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#717182", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#13131E",
                  border: "1px solid rgba(255,255,255,0.08)",
                  borderRadius: "12px",
                }}
              />
              <Area type="monotone" dataKey="ig" stroke="#E1306C" strokeWidth={2} fill="url(#gIg)" name="Instagram" />
              <Area type="monotone" dataKey="tt" stroke="#06B6D4" strokeWidth={2} fill="url(#gTt)" name="TikTok" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-2xl border border-white/5 bg-[#0F0F1C] p-5">
          <h3 className="mb-4 text-sm font-bold text-white">Engagement Rate by Day (%)</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={ENGAGEMENT_DATA} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
              <XAxis dataKey="day" tick={{ fill: "#717182", fontSize: 11 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: "#717182", fontSize: 11 }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#13131E",
                  border: "1px solid rgba(255,255,255,0.08)",
                  borderRadius: "12px",
                }}
                cursor={{ fill: "rgba(139,92,246,0.08)" }}
              />
              <Bar dataKey="rate" fill="#8B5CF6" radius={[4, 4, 0, 0]} name="Eng. Rate" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
