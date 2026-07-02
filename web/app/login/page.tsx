"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Check, ChevronRight, Globe, RefreshCw, Sparkles } from "lucide-react";

import { login } from "../../lib/api";
import { setSession } from "../../lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("daniela@creatoros.demo");
  const [password, setPassword] = useState("demo1234");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await login(email, password);
      setSession({
        accessToken: result.access_token,
        userId: result.user_id,
        email,
      });
      router.replace("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign in failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-[#08080F]" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
      <div className="relative hidden w-[46%] flex-col justify-between overflow-hidden bg-gradient-to-br from-[#1C0845] via-[#0E0425] to-[#08080F] p-12 lg:flex">
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute left-16 top-24 h-72 w-72 rounded-full bg-violet-700 opacity-25 blur-[110px]" />
          <div className="absolute bottom-32 right-8 h-52 w-52 rounded-full bg-pink-600 opacity-20 blur-[90px]" />
          <div className="absolute left-1/2 top-1/2 h-96 w-96 -translate-x-1/2 -translate-y-1/2 rounded-full bg-indigo-800 opacity-10 blur-[140px]" />
        </div>
        <div className="relative z-10 flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-violet-600 shadow-lg shadow-violet-900/50">
            <Sparkles size={17} className="text-white" />
          </div>
          <span className="text-xl font-bold tracking-tight text-white">CreatorOS</span>
        </div>
        <div className="relative z-10">
          <h1 className="mb-5 text-[2.6rem] font-extrabold leading-[1.15] text-white">
            Your AI-powered
            <br />
            creator studio
          </h1>
          <p className="mb-10 text-lg leading-relaxed text-violet-200/60">
            Trend research, content generation, audience insights — unified in one platform.
          </p>
          <div className="space-y-3.5">
            {[
              "Trend Research Agent spots viral topics before they peak",
              "Content Generator writes platform-native scripts & captions",
              "Growth Coach delivers weekly personalized strategy",
            ].map((feat) => (
              <div key={feat} className="flex items-start gap-3">
                <div className="mt-0.5 flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full border border-violet-400/30 bg-violet-500/20">
                  <Check size={9} className="text-violet-300" />
                </div>
                <span className="text-sm leading-snug text-white/65">{feat}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="relative z-10 flex items-center gap-3">
          <div className="flex -space-x-2">
            {[
              ["D", "#7C3AED"],
              ["M", "#EC4899"],
              ["S", "#06B6D4"],
              ["K", "#10B981"],
            ].map(([initial, color]) => (
              <div
                key={initial}
                className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-[#0E0425] text-xs font-bold text-white"
                style={{ backgroundColor: color }}
              >
                {initial}
              </div>
            ))}
          </div>
          <p className="text-sm text-white/45">
            <span className="font-semibold text-white">2,400+</span> creators growing with AI
          </p>
        </div>
      </div>

      <div className="flex flex-1 items-center justify-center p-8">
        <div className="w-full max-w-[380px]">
          <div className="mb-10 flex items-center gap-2 lg:hidden">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-violet-600">
              <Sparkles size={15} className="text-white" />
            </div>
            <span className="text-lg font-bold text-white">CreatorOS</span>
          </div>
          <h2 className="mb-1 text-2xl font-bold text-white">Welcome back</h2>
          <p className="mb-8 text-sm text-[#717182]">Sign in to your creator dashboard</p>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="mb-1.5 block text-[11px] font-semibold uppercase tracking-widest text-[#A0A0B8]">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="daniela@creatoros.demo"
                className="w-full rounded-xl border border-white/8 bg-[#0F0F1C] px-4 py-3 text-sm text-white transition-all placeholder:text-[#717182] focus:border-violet-500/50 focus:outline-none focus:ring-1 focus:ring-violet-500/25"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-[11px] font-semibold uppercase tracking-widest text-[#A0A0B8]">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full rounded-xl border border-white/8 bg-[#0F0F1C] px-4 py-3 text-sm text-white transition-all placeholder:text-[#717182] focus:border-violet-500/50 focus:outline-none focus:ring-1 focus:ring-violet-500/25"
              />
            </div>
            {error ? <p className="text-sm text-red-400">{error}</p> : null}
            <div className="flex items-center justify-between">
              <label className="flex cursor-pointer select-none items-center gap-2">
                <div className="h-4 w-4 rounded border border-white/15 bg-[#0F0F1C]" />
                <span className="text-xs text-[#717182]">Remember me</span>
              </label>
              <button type="button" className="text-xs text-violet-400 transition-colors hover:text-violet-300">
                Forgot password?
              </button>
            </div>
            <button
              type="submit"
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-violet-600 py-3.5 text-sm font-semibold text-white shadow-lg shadow-violet-900/40 transition-all hover:bg-violet-500 active:bg-violet-700 disabled:opacity-70"
            >
              {loading ? (
                <RefreshCw size={15} className="animate-spin" />
              ) : (
                <>
                  Sign in <ChevronRight size={15} />
                </>
              )}
            </button>
          </form>
          <p className="mt-6 text-center text-sm text-[#717182]">
            {"Don't have an account? "}
            <button type="button" className="font-medium text-violet-400 transition-colors hover:text-violet-300">
              Start free trial
            </button>
          </p>
          <div className="mt-8">
            <div className="mb-4 flex items-center gap-3">
              <div className="h-px flex-1 bg-white/7" />
              <span className="text-[10px] font-semibold uppercase tracking-widest text-[#717182]">
                Or continue with
              </span>
              <div className="h-px flex-1 bg-white/7" />
            </div>
            <div className="grid grid-cols-1 gap-3">
              {["Google"].map((provider) => (
                <button
                  key={provider}
                  type="button"
                  className="flex items-center justify-center gap-2 rounded-xl border border-white/8 bg-[#0F0F1C] py-2.5 text-sm text-white/60 transition-all hover:border-white/20 hover:text-white"
                >
                  <Globe size={13} />
                  {provider}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
