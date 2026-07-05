"use client";

import type { ReactNode } from "react";
import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Bell, Check, Globe, Loader2, Zap } from "lucide-react";

import { getSession } from "../../lib/auth";
import {
  disconnectPlatform,
  getPlatformConnections,
  getProfile,
  startPlatformConnection,
  updateUser,
  type CreatorProfile,
  type PlatformConnection,
} from "../../lib/api";
import { IgIcon, TtIcon, YtIcon } from "../ui/platform-icons";

const PLATFORM_ICONS: Record<string, ReactNode> = {
  instagram: <IgIcon size={20} />,
  tiktok: <TtIcon size={20} />,
  youtube: <YtIcon size={20} />,
  pinterest: <Globe size={18} className="text-[#717182]" />,
};

const NOTIFICATION_PREFS_KEY = "creatoros.notification_prefs";

const NOTIFICATION_OPTIONS = [
  {
    id: "new_subscriber_alerts",
    label: "New subscriber alerts",
    description: "Get notified when someone subscribes to your content.",
  },
  {
    id: "review_moderation_queue",
    label: "Review moderation queue",
    description: "Alerts when comments or reviews need moderation.",
  },
  {
    id: "weekly_revenue_digest",
    label: "Weekly revenue digest",
    description: "A summary of earnings, tips, and brand deals each week.",
  },
  {
    id: "payout_confirmations",
    label: "Payout confirmations",
    description: "Confirmations when payouts are initiated or deposited.",
  },
] as const;

type NotificationPrefId = (typeof NOTIFICATION_OPTIONS)[number]["id"];
type NotificationPrefs = Record<NotificationPrefId, boolean>;

const DEFAULT_NOTIFICATION_PREFS: NotificationPrefs = {
  new_subscriber_alerts: true,
  review_moderation_queue: true,
  weekly_revenue_digest: true,
  payout_confirmations: true,
};

function loadNotificationPrefs(): NotificationPrefs {
  if (typeof window === "undefined") return DEFAULT_NOTIFICATION_PREFS;
  try {
    const raw = window.localStorage.getItem(NOTIFICATION_PREFS_KEY);
    if (!raw) return DEFAULT_NOTIFICATION_PREFS;
    const parsed = JSON.parse(raw) as Partial<NotificationPrefs>;
    return { ...DEFAULT_NOTIFICATION_PREFS, ...parsed };
  } catch {
    return DEFAULT_NOTIFICATION_PREFS;
  }
}

export function SettingsScreen() {
  const [activeModel, setActiveModel] = useState("claude");
  const [profile, setProfile] = useState<CreatorProfile | null>(null);
  const [userInput, setUserInput] = useState("");
  const [savingUser, setSavingUser] = useState(false);
  const [userMessage, setUserMessage] = useState<string | null>(null);
  const [userError, setUserError] = useState<string | null>(null);
  const [platforms, setPlatforms] = useState<PlatformConnection[]>([]);
  const [loadingPlatforms, setLoadingPlatforms] = useState(true);
  const [connectingPlatform, setConnectingPlatform] = useState<string | null>(null);
  const [disconnectingPlatform, setDisconnectingPlatform] = useState<string | null>(null);
  const [platformMessage, setPlatformMessage] = useState<string | null>(null);
  const [notificationPrefs, setNotificationPrefs] = useState<NotificationPrefs>(
    DEFAULT_NOTIFICATION_PREFS,
  );
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
    void getProfile().then((result) => {
      if (!result) return;
      setProfile(result);
      setUserInput(result.user ?? result.handle);
    });
  }, []);

  useEffect(() => {
    setNotificationPrefs(loadNotificationPrefs());
  }, []);

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

  const handleSaveUser = async () => {
    const trimmed = userInput.trim().replace(/^@+/, "");
    if (!trimmed) {
      setUserError("User name is required.");
      return;
    }

    setSavingUser(true);
    setUserError(null);
    setUserMessage(null);
    try {
      const updated = await updateUser(trimmed);
      setProfile(updated);
      setUserInput(updated.user);
      setUserMessage("User name updated.");
    } catch (error) {
      setUserError(error instanceof Error ? error.message : "Failed to update user name.");
    } finally {
      setSavingUser(false);
    }
  };

  const userChanged =
    profile !== null &&
    trimmedUser(userInput) !== (profile.user ?? profile.handle);

  function trimmedUser(value: string) {
    return value.trim().replace(/^@+/, "").toLowerCase();
  }

  const toggleNotification = (id: NotificationPrefId) => {
    setNotificationPrefs((current) => {
      const next = { ...current, [id]: !current[id] };
      window.localStorage.setItem(NOTIFICATION_PREFS_KEY, JSON.stringify(next));
      return next;
    });
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
        <div className="mb-1 flex items-center gap-2">
          <Bell size={14} className="text-violet-400" />
          <h3 className="text-sm font-bold text-white">Notifications</h3>
        </div>
        <p className="mb-4 text-xs text-[#717182]">
          Choose which updates you receive by email and in-app.
        </p>
        <div className="space-y-2">
          {NOTIFICATION_OPTIONS.map((option) => {
            const enabled = notificationPrefs[option.id];
            return (
              <button
                key={option.id}
                type="button"
                onClick={() => toggleNotification(option.id)}
                className={`flex w-full items-start gap-4 rounded-xl border px-4 py-3 text-left transition-all ${
                  enabled
                    ? "border-violet-500/25 bg-violet-500/10"
                    : "border-white/5 bg-white/[0.02] hover:border-white/12"
                }`}
              >
                <div
                  className={`mt-0.5 h-3.5 w-3.5 flex-shrink-0 rounded-full border-2 transition-all ${
                    enabled ? "border-violet-400 bg-violet-400" : "border-white/20"
                  }`}
                />
                <div className="flex-1">
                  <p className="text-sm font-semibold text-white">{option.label}</p>
                  <p className="text-xs text-[#717182]">{option.description}</p>
                </div>
                {enabled ? <Check size={14} className="mt-0.5 flex-shrink-0 text-violet-400" /> : null}
              </button>
            );
          })}
        </div>
      </div>

      <div className="rounded-2xl border border-white/5 bg-[#0F0F1C] p-5">
        <h3 className="mb-4 text-sm font-bold text-white">Account</h3>
        <div className="space-y-4">
          <div>
            <label htmlFor="settings-user" className="mb-2 block text-xs text-[#717182]">
              User
            </label>
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
              <div className="flex min-w-0 flex-1 items-center rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2">
                <span className="mr-1 text-sm text-violet-300">@</span>
                <input
                  id="settings-user"
                  type="text"
                  value={userInput}
                  onChange={(e) => {
                    setUserInput(e.target.value.replace(/^@+/, ""));
                    setUserError(null);
                    setUserMessage(null);
                  }}
                  placeholder="your.name"
                  className="w-full bg-transparent text-sm text-white outline-none placeholder:text-[#717182]"
                  autoComplete="username"
                  spellCheck={false}
                />
              </div>
              <button
                type="button"
                disabled={savingUser || !userChanged}
                onClick={() => void handleSaveUser()}
                className="rounded-full bg-violet-600 px-4 py-2 text-xs font-semibold text-white transition-all hover:bg-violet-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {savingUser ? "Saving..." : "Save"}
              </button>
            </div>
            {userError ? (
              <p className="mt-2 text-xs text-red-300">{userError}</p>
            ) : userMessage ? (
              <p className="mt-2 text-xs text-emerald-300">{userMessage}</p>
            ) : (
              <p className="mt-2 text-xs text-[#717182]">
                Your public user name must be unique. Letters, numbers, dots, and underscores only.
              </p>
            )}
          </div>

          {[
            { label: "Email", value: session?.email ?? "—" },
            { label: "Plan", value: "Pro · $49/mo" },
            { label: "API", value: process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api/v1" },
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
