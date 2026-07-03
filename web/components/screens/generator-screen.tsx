"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { Check, Copy, RefreshCw, Sparkles, Wand2 } from "lucide-react";

import {
  createCalendarItem,
  generateIdea,
  getActiveUserId,
  getProfile,
  saveIdea,
} from "../../lib/api";
import { IgIcon, TtIcon, YtIcon } from "../ui/platform-icons";

type Platform = "instagram" | "tiktok" | "youtube";

export function GeneratorScreen() {
  const searchParams = useSearchParams();
  const [plat, setPlat] = useState<Platform>("instagram");
  const [cType, setCType] = useState("Caption");
  const [topic, setTopic] = useState("");
  const [tone, setTone] = useState("Authentic");
  const [audience, setAudience] = useState("");
  const [goal, setGoal] = useState("engagement");
  const [generating, setGenerating] = useState(false);
  const [saveLoading, setSaveLoading] = useState(false);
  const [generated, setGenerated] = useState("");
  const [copied, setCopied] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    const initialTopic = searchParams.get("topic");
    if (initialTopic) setTopic(initialTopic);
    const userId = getActiveUserId();
    void getProfile(userId)
      .then((profile) => {
        if (!profile) return;
        if (profile.niche) setAudience(profile.niche);
        if (profile.creator_voice) setTone(profile.creator_voice.split(",")[0]?.trim() ?? "Authentic");
      })
      .catch(() => undefined);
  }, [searchParams]);

  const handleGenerate = async () => {
    if (!topic.trim()) return;
    setGenerating(true);
    setGenerated("");
    setSaved(false);
    try {
      const result = await generateIdea({
        topic,
        platform: plat,
        creator_voice: tone,
        goal,
        audience: audience || "general audience",
      });
      const output = [
        `Hook: ${result.title}`,
        "",
        result.description,
        "",
        `Suggested score: ${Math.round(result.suggested_score)}`,
        `Platform: ${plat}`,
        `Tone: ${tone}`,
      ].join("\n");
      setGenerated(output);
    } catch {
      setGenerated("Generation failed. Check that the API is running and try again.");
    } finally {
      setGenerating(false);
    }
  };

  const handleCopy = async () => {
    await navigator.clipboard.writeText(generated);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSave = async () => {
    if (!generated.trim()) return;
    setSaveLoading(true);
    try {
      const userId = getActiveUserId();
      const idea = await saveIdea({
        user_id: userId,
        title: topic || "Generated content",
        description: generated,
        status: "draft",
      });
      const scheduled = new Date();
      scheduled.setDate(scheduled.getDate() + 1);
      scheduled.setHours(9, 0, 0, 0);
      await createCalendarItem({
        user_id: userId,
        content_idea_id: idea.id,
        platform: plat,
        scheduled_for: scheduled.toISOString(),
        status: "scheduled",
        notes: topic || idea.title,
      });
      setSaved(true);
    } finally {
      setSaveLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="mb-1 text-[1.65rem] font-extrabold text-white">Content Generator</h1>
        <p className="text-sm text-[#717182]">AI-powered captions, scripts & hooks — native to each platform</p>
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="space-y-4">
          <div className="rounded-2xl border border-white/5 bg-[#0F0F1C] p-5">
            <p className="mb-3 text-[10px] font-bold uppercase tracking-widest text-[#717182]">Platform</p>
            <div className="flex gap-2">
              {[
                { id: "instagram" as const, icon: <IgIcon size={18} />, label: "Instagram" },
                { id: "tiktok" as const, icon: <TtIcon size={18} />, label: "TikTok" },
                { id: "youtube" as const, icon: <YtIcon size={18} />, label: "YouTube" },
              ].map((p) => (
                <button
                  key={p.id}
                  type="button"
                  onClick={() => setPlat(p.id)}
                  className={`flex flex-1 flex-col items-center gap-2 rounded-xl border py-3.5 transition-all ${
                    plat === p.id ? "border-violet-500/35 bg-violet-500/10" : "border-white/7 bg-white/2 hover:border-white/15"
                  }`}
                >
                  {p.icon}
                  <span className="text-xs text-white/65">{p.label}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="rounded-2xl border border-white/5 bg-[#0F0F1C] p-5">
            <p className="mb-3 text-[10px] font-bold uppercase tracking-widest text-[#717182]">Content type</p>
            <div className="flex flex-wrap gap-2">
              {["Caption", "Script", "Hook", "Bio", "CTA", "Thread"].map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setCType(t)}
                  className={`rounded-full px-3 py-1.5 text-sm font-medium transition-all ${
                    cType === t ? "bg-violet-600 text-white" : "bg-white/5 text-[#717182] hover:text-white"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-4 rounded-2xl border border-white/5 bg-[#0F0F1C] p-5">
            <div>
              <p className="mb-2 text-[10px] font-bold uppercase tracking-widest text-[#717182]">Topic / Brief</p>
              <textarea
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g. My morning routine that changed my life..."
                className="w-full resize-none rounded-xl border border-white/8 bg-white/3 px-4 py-3 text-sm text-white placeholder:text-[#717182] focus:border-violet-500/50 focus:outline-none"
                rows={4}
              />
            </div>
            <div>
              <p className="mb-2 text-[10px] font-bold uppercase tracking-widest text-[#717182]">Audience</p>
              <input
                value={audience}
                onChange={(e) => setAudience(e.target.value)}
                className="w-full rounded-xl border border-white/8 bg-white/3 px-4 py-3 text-sm text-white placeholder:text-[#717182] focus:border-violet-500/50 focus:outline-none"
                placeholder="Who is this for?"
              />
            </div>
            <div>
              <p className="mb-2 text-[10px] font-bold uppercase tracking-widest text-[#717182]">Goal</p>
              <input
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                className="w-full rounded-xl border border-white/8 bg-white/3 px-4 py-3 text-sm text-white placeholder:text-[#717182] focus:border-violet-500/50 focus:outline-none"
                placeholder="engagement, saves, followers..."
              />
            </div>
            <div>
              <p className="mb-2 text-[10px] font-bold uppercase tracking-widest text-[#717182]">Tone</p>
              <div className="flex flex-wrap gap-2">
                {["Authentic", "Educational", "Entertaining", "Emotional", "Bold"].map((t) => (
                  <button
                    key={t}
                    type="button"
                    onClick={() => setTone(t)}
                    className={`rounded-full px-3 py-1.5 text-xs font-medium transition-all ${
                      tone === t
                        ? "border border-cyan-500/25 bg-cyan-600/25 text-cyan-300"
                        : "bg-white/5 text-[#717182] hover:text-white"
                    }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <button
            type="button"
            onClick={() => void handleGenerate()}
            disabled={generating || !topic.trim()}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-pink-600 py-3.5 text-sm font-semibold text-white shadow-lg shadow-violet-900/30 transition-all hover:from-violet-500 hover:to-pink-500 disabled:opacity-50"
          >
            {generating ? <RefreshCw size={15} className="animate-spin" /> : <Wand2 size={15} />}
            {generating ? "Generating..." : "Generate Content"}
          </button>
        </div>

        <div className="flex min-h-[420px] flex-col rounded-2xl border border-white/5 bg-[#0F0F1C]">
          <div className="flex items-center justify-between border-b border-white/5 px-5 py-4">
            <div className="flex items-center gap-2">
              <Sparkles size={13} className="text-violet-400" />
              <span className="text-sm font-semibold text-white">Generated Content</span>
            </div>
            <div className="flex items-center gap-3">
              {generated ? (
                <button
                  type="button"
                  onClick={() => void handleCopy()}
                  className="flex items-center gap-1.5 text-xs text-[#717182] transition-colors hover:text-white"
                >
                  {copied ? <Check size={12} className="text-emerald-400" /> : <Copy size={12} />}
                  {copied ? "Copied!" : "Copy"}
                </button>
              ) : null}
            </div>
          </div>
          <div className="scrollbar-hide flex-1 overflow-y-auto p-5">
            {!generated && !generating ? (
              <div className="flex h-full items-center justify-center">
                <div className="text-center">
                  <Wand2 size={30} className="mx-auto mb-3 text-violet-500/25" />
                  <p className="text-sm text-[#717182]">Your content will appear here</p>
                  <p className="mt-1 text-xs text-[#717182]/50">Fill in the brief and click Generate</p>
                </div>
              </div>
            ) : (
              <pre className="whitespace-pre-wrap text-sm leading-relaxed text-white/85">{generated}
                {generating ? <span className="animate-pulse text-violet-400">▋</span> : null}
              </pre>
            )}
          </div>
          {generated ? (
            <div className="border-t border-white/5 p-4">
              <button
                type="button"
                onClick={() => void handleSave()}
                disabled={saveLoading || saved}
                className="w-full rounded-xl bg-violet-600 py-3 text-sm font-semibold text-white transition-all hover:bg-violet-500 disabled:opacity-60"
              >
                {saveLoading ? "Saving..." : saved ? "Saved to Calendar" : "Save to Calendar"}
              </button>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
