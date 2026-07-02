"use client";

import type { ReactNode } from "react";
import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Check, Globe, Loader2, Zap } from "lucide-react";

import { getSession } from "../../lib/auth";
import {
  disconnectPlatform,
  getPlatformConnections,
  startPlatformConnection,
  type PlatformConnection,
} from "../../lib/api";
import { IgIcon, TtIcon, YtIcon } from "../ui/platform-icons";

const PLATFORM_ICONS: Record<string, ReactNode> = {
  instagram: <IgIcon size={20} />,
  tiktok: <TtIcon size={20} />,
  youtube: <YtIcon size={20} />,
  pinterest: <Globe size={18} className="text-[#717182]" />,
};

export function SettingsScreen() {
  const [activeModel, setActiveModel] = useState("claude");
  const [platforms, setPlatforms] = useState<PlatformConnection[]>([]);
  const [loadingPlatforms, setLoadingPlatforms] = useState(true);
  const [connectingPlatform, setConnectingPlatform] = useState<string | null>(null);
  const [disconnectingPlatform, setDisconnectingPlatform] = useState<string | null>(null);
  const [platformMessage, setPlatformMessage] = useState<string | null>(null);
  const searchParams = useSearchParams();
  const session = getSession();

  const loadPlatforms = useCallback(async () => {
    setLoadingPlatforms(true);
    try {
      const result = await getPlatformConnections();
      setPlatforms(result.platforms);
    } catch (error) {
      setPlatformMessage(error instanceof Error ? error.message : "Failed to load platforms.");
    } finally {
      setLoadingPlatforms(false);
    }
  }, []);

  useEffect(() => {
    void loadPlatforms();
  }, [loadPlatforms]);

  useEffect(() => {
    const status = searchParams.get("status");
    const platform = searchParams.get("platform");
    const message = searchParams.get("message");

    if (!status || !platform) return;

    if (status === "connected") {
      setPlatformMessage(`${platform.charAt(0).toUpperCase()}${platform.slice(1)} connected successfully.`);
      void loadPlatforms();
    } else if (status === "error") {
      setPlatformMessage(message ?? `Failed to connect ${platform}.`);
    }

    const url = new URL(window.location.href);
    url.searchParams.delete("status");
    url.searchParams.delete("platform");
    url.searchParams.delete("message");
    window.history.replaceState({}, "", url.toString());
  }, [loadPlatforms, searchParams]);

  const handleConnect = async (platform: string) => {
    setConnectingPlatform(platform);
    setPlatformMessage(null);
    try {
      const result = await startPlatformConnection(platform);
      window.location.href = result.authorization_url;
    } catch (error) {
      setPlatformMessage(error instanceof Error ? error.message : "Failed to start connection.");
      setConnectingPlatform(null);
    }
  };

  const handleDisconnect = async (platform: string) => {
    setDisconnectingPlatform(platform);
    setPlatformMessage(null);
    try {
      await disconnectPlatform(platform);
      await loadPlatforms();
      setPlatformMessage(`${platform.charAt(0).toUpperCase()}${platform.slice(1)} disconnected.`);
    } catch (error) {
      setPlatformMessage(error instanceof Error ? error.message : "Failed to disconnect platform.");
    } finally {
      setDisconnectingPlatform(null);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="mb-1 text-[1.65rem] font-extrabold text-white">Settings</h1>
        <p className="text-sm text-[#717182]">Manage your account, AI providers, and integrations</p>
      </div>

      <div className="rounded-2xl border border-white/5 bg-[#0F0F1C] p-5">
        <div className="mb-1 flex items-center gap-2">
          <Zap size={14} className="text-violet-400" />
          <h3 className="text-sm font-bold text-white">AI Provider Abstraction</h3>
        </div>
        <p className="mb-5 text-xs text-[#717182]">
          Switch AI models powering your agents without losing context or rebuilding prompts
        </p>
        <div className="space-y-2">
          {[
            { id: "claude", name: "Claude 3.5 Sonnet", provider: "Anthropic", badge: "Recommended" },
            { id: "gpt4o", name: "GPT-4o", provider: "OpenAI", badge: null },
            { id: "gemini", name: "Gemini 1.5 Pro", provider: "Google", badge: null },
            { id: "llama", name: "Llama 3.1 70B", provider: "Meta · Self-hosted", badge: "Open source" },
          ].map((m) => (
            <button
              key={m.id}
              type="button"
              onClick={() => setActiveModel(m.id)}
              className={`flex w-full items-center gap-4 rounded-xl border px-4 py-3 transition-all ${
                activeModel === m.id
                  ? "border-violet-500/35 bg-violet-500/10"
                  : "border-white/5 bg-white/[0.02] hover:border-white/12"
              }`}
            >
              <div
                className={`h-3.5 w-3.5 flex-shrink-0 rounded-full border-2 transition-all ${
                  activeModel === m.id ? "border-violet-400 bg-violet-400" : "border-white/20"
                }`}
              />
              <div className="flex-1 text-left">
                <p className="text-sm font-semibold text-white">{m.name}</p>
                <p className="text-xs text-[#717182]">{m.provider}</p>
              </div>
              {m.badge ? (
                <span className="rounded-full border border-violet-500/20 bg-violet-500/15 px-2 py-0.5 text-[11px] font-medium text-violet-300">
                  {m.badge}
                </span>
              ) : null}
              {activeModel === m.id ? <Check size={14} className="flex-shrink-0 text-violet-400" /> : null}
            </button>
          ))}
        </div>
      </div>

      <div className="rounded-2xl border border-white/5 bg-[#0F0F1C] p-5">
        <h3 className="mb-1 text-sm font-bold text-white">Connected Platforms</h3>
        <p className="mb-4 text-xs text-[#717182]">
          Connect real accounts via OAuth. Add provider credentials to <code className="text-violet-300">api/.env.local</code> to enable each platform.
        </p>

        {platformMessage ? (
          <div className="mb-4 rounded-xl border border-violet-500/20 bg-violet-500/10 px-3 py-2 text-xs text-violet-200">
            {platformMessage}
          </div>
        ) : null}

        <div className="space-y-3">
          {loadingPlatforms ? (
            <div className="flex items-center gap-2 text-sm text-[#717182]">
              <Loader2 size={14} className="animate-spin" />
              Loading platforms...
            </div>
          ) : (
            platforms.map((platform) => {
              const isConnecting = connectingPlatform === platform.platform;
              const isDisconnecting = disconnectingPlatform === platform.platform;
              const busy = isConnecting || isDisconnecting;

              return (
                <div key={platform.platform} className="flex items-center gap-3">
                  {PLATFORM_ICONS[platform.platform] ?? <Globe size={18} className="text-[#717182]" />}
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-white">{platform.name}</p>
                    {platform.connected && platform.account_handle ? (
                      <p className="text-xs text-[#717182]">{platform.account_handle}</p>
                    ) : !platform.configured ? (
                      <p className="text-xs text-amber-300/80">OAuth credentials not configured</p>
                    ) : (
                      <p className="text-xs text-[#717182]">Not connected</p>
                    )}
                  </div>
                  <button
                    type="button"
                    disabled={busy || (!platform.connected && !platform.configured)}
                    onClick={() =>
                      platform.connected
                        ? void handleDisconnect(platform.platform)
                        : void handleConnect(platform.platform)
                    }
                    className={`rounded-full px-3 py-1.5 text-xs font-semibold transition-all disabled:cursor-not-allowed disabled:opacity-60 ${
                      platform.connected
                        ? "border border-emerald-500/20 bg-emerald-500/15 text-emerald-300 hover:border-red-500/20 hover:bg-red-500/10 hover:text-red-300"
                        : "bg-white/5 text-[#717182] hover:text-white"
                    }`}
                  >
                    {busy ? (
                      <span className="inline-flex items-center gap-1">
                        <Loader2 size={12} className="animate-spin" />
                        {platform.connected ? "Disconnecting" : "Connecting"}
                      </span>
                    ) : platform.connected ? (
                      "Disconnect"
                    ) : (
                      "Connect"
                    )}
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>

      <div className="rounded-2xl border border-white/5 bg-[#0F0F1C] p-5">
        <h3 className="mb-4 text-sm font-bold text-white">Account</h3>
        <div className="space-y-3">
          {[
            { label: "Email", value: session?.email ?? "—" },
            { label: "User ID", value: session?.userId ?? "—" },
            { label: "Plan", value: "Pro · $49/mo" },
            { label: "API", value: process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1" },
          ].map((row) => (
            <div key={row.label} className="flex items-center justify-between border-b border-white/5 py-2 last:border-0">
              <span className="text-xs text-[#717182]">{row.label}</span>
              <span className="max-w-[60%] truncate text-sm font-medium text-white">{row.value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
