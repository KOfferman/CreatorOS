"use client";

import { useEffect, useState } from "react";
import { Check, Edit3 } from "lucide-react";

import { getIdeas, getProfile, getTrends, type CreatorProfile } from "../../lib/api";
import { IgIcon, TtIcon, YtIcon } from "../ui/platform-icons";

export function ProfileScreen() {
  const [profile, setProfile] = useState<CreatorProfile | null>(null);
  const [creatorScore, setCreatorScore] = useState(371);

  useEffect(() => {
    void Promise.all([getProfile(), getIdeas(), getTrends()]).then(
      ([p, ideas, trends]) => {
        if (!p) return;
        setProfile(p);
        setCreatorScore(
          Math.min(
            500,
            Math.round((p.audience_size ?? 0) / 30000 + trends.trends.length * 8 + ideas.ideas.length * 5),
          ),
        );
      },
    ).catch(() => undefined);
  }, []);

  const username = profile?.user ?? profile?.handle ?? "creator";
  const voiceTags = (profile?.creator_voice ?? "Authentic, Warm, Honest").split(",").map((v) => v.trim());

  return (
    <div className="space-y-6">
      <div>
        <h1 className="mb-1 text-[1.65rem] font-extrabold text-white">Creator Profile</h1>
        <p className="text-sm text-[#717182]">Your public presence and content identity</p>
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="rounded-2xl border border-white/5 bg-[#0F0F1C] p-6 text-center">
          <div className="relative mb-4 inline-block">
            <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-600 via-pink-500 to-orange-400 text-3xl font-extrabold uppercase text-white">
              {username.charAt(0)}
            </div>
            <div className="absolute -bottom-1 -right-1 flex h-6 w-6 items-center justify-center rounded-full border-2 border-[#0F0F1C] bg-emerald-500">
              <Check size={10} className="text-white" />
            </div>
          </div>
          <h2 className="mb-0.5 text-lg font-bold text-white">@{username}</h2>
          <p className="mb-3 text-xs text-[#717182]">{profile?.niche ?? "Creator"}</p>
          <div className="mb-5 flex justify-center gap-2">
            <IgIcon size={20} />
            <TtIcon size={20} />
            <YtIcon size={20} />
          </div>
          <div className="rounded-xl border border-violet-500/20 bg-gradient-to-r from-violet-600/20 to-pink-600/20 px-4 py-3">
            <p className="text-2xl font-bold text-white" style={{ fontFamily: "'JetBrains Mono', monospace" }}>
              {creatorScore}
            </p>
            <p className="text-xs text-violet-300/60">Creator Score · Top 8%</p>
          </div>
        </div>

        <div className="space-y-4 lg:col-span-2">
          <div className="rounded-2xl border border-white/5 bg-[#0F0F1C] p-5">
            <div className="mb-3 flex items-center justify-between">
              <p className="text-[10px] font-bold uppercase tracking-widest text-[#717182]">Bio</p>
              <button type="button" className="flex items-center gap-1 text-xs text-violet-400 transition-colors hover:text-violet-300">
                <Edit3 size={10} /> Edit
              </button>
            </div>
            <p className="text-sm leading-relaxed text-white/80">
              {profile?.bio ?? "Add your creator bio in profile settings."}
            </p>
          </div>

          <div className="rounded-2xl border border-white/5 bg-[#0F0F1C] p-5">
            <p className="mb-3 text-[10px] font-bold uppercase tracking-widest text-[#717182]">My Voice</p>
            <div className="flex flex-wrap gap-2">
              {voiceTags.map((tag) => (
                <span
                  key={tag}
                  className="rounded-full border border-violet-500/20 bg-violet-500/10 px-3 py-1 text-xs text-violet-300"
                >
                  {tag}
                </span>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-white/5 bg-[#0F0F1C] p-5">
            <p className="mb-3 text-[10px] font-bold uppercase tracking-widest text-[#717182]">Content Pillars</p>
            <div className="grid grid-cols-2 gap-2">
              {[
                { label: "Personal story", pct: 40 },
                { label: "Education & tutorials", pct: 25 },
                { label: "Aspiration", pct: 25 },
                { label: "Community & collab", pct: 10 },
              ].map((p) => (
                <div key={p.label} className="rounded-xl bg-white/3 p-3">
                  <p className="mb-2 text-xs text-white/70">{p.label}</p>
                  <div className="flex items-center gap-2">
                    <div className="h-1.5 flex-1 rounded-full bg-white/5">
                      <div className="h-full rounded-full bg-violet-500" style={{ width: `${p.pct}%` }} />
                    </div>
                    <span className="text-xs font-semibold text-violet-300">{p.pct}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
