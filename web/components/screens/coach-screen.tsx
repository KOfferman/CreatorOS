"use client";

import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Bot, Send, Trash2 } from "lucide-react";

import { ApiRequestError, askCoach } from "../../lib/api";
import { clearSession } from "../../lib/auth";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: string;
};

function newMessage(role: "user" | "assistant", content: string): Message {
  return {
    id: crypto.randomUUID(),
    role,
    content,
    createdAt: new Date().toISOString(),
  };
}

const HISTORY_KEY = "creatoros.coach.history.v1";
const WELCOME_MESSAGE = newMessage(
  "assistant",
  "Hey! 👋 I've analyzed your recent content signals. Ready to push your growth even higher?",
);

function isStaleCoachError(content: string): boolean {
  const lowered = content.toLowerCase();
  return (
    lowered.includes("couldn't reach the coach") ||
    lowered.includes("cannot reach the api") ||
    lowered.includes("missing bearer token") ||
    lowered.includes("coach llm unavailable") ||
    lowered.includes("verify the api is running")
  );
}

function loadCoachHistory(): Message[] {
  if (typeof window === "undefined") return [WELCOME_MESSAGE];
  try {
    const raw = window.localStorage.getItem(HISTORY_KEY);
    if (!raw) return [WELCOME_MESSAGE];
    const parsed = JSON.parse(raw) as Message[];
    if (!Array.isArray(parsed) || !parsed.length) return [WELCOME_MESSAGE];
    const cleaned = parsed.filter((msg) => !(msg.role === "assistant" && isStaleCoachError(msg.content)));
    return cleaned.length ? cleaned : [WELCOME_MESSAGE];
  } catch {
    return [WELCOME_MESSAGE];
  }
}

const SUGGESTED_QUESTIONS = [
  "Why is my reach dropping?",
  "Best posting times for my audience",
  "How to improve my hook rate",
  "Content pillars for my niche",
];

export function CoachScreen() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>(() => loadCoachHistory());
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [llmLabel, setLlmLabel] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const persistable = messages.filter(
      (msg) => !(msg.role === "assistant" && isStaleCoachError(msg.content)),
    );
    localStorage.setItem(HISTORY_KEY, JSON.stringify(persistable));
  }, [messages]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const send = async (text: string) => {
    if (!text.trim() || loading) return;
    const userMessage = newMessage("user", text);
    setMessages((m) => [...m, userMessage]);
    setInput("");
    setLoading(true);
    try {
      const response = await askCoach({ question: text });
      if (response.llm_provider) {
        const label =
          response.llm_provider === "mock"
            ? "Demo mode (mock responses)"
            : response.llm_provider === "openrouter"
              ? `Hermes via OpenRouter · ${response.llm_model ?? "cloud"}`
              : `${response.llm_provider} · ${response.llm_model ?? "model"}`;
        setLlmLabel(label);
      }
      const body = [
        response.direct_coaching_response,
        response.recommended_next_actions.length
          ? `\n\n**Next actions:**\n${response.recommended_next_actions.map((a) => `- ${a}`).join("\n")}`
          : "",
        response.risk_warning ? `\n\n⚠️ ${response.risk_warning}` : "",
      ].join("");
      setMessages((m) => [...m, newMessage("assistant", body)]);
    } catch (error) {
      if (error instanceof ApiRequestError && error.status === 401) {
        clearSession();
        router.replace("/login");
        return;
      }
      const message =
        error instanceof Error
          ? error.message
          : "I couldn't reach the coach service. Please verify the API is running with `cd api && make dev`.";
      setMessages((m) => [...m, newMessage("assistant", message)]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    if (loading) return;
    setInput("");
    setMessages([WELCOME_MESSAGE]);
    localStorage.removeItem(HISTORY_KEY);
  };

  return (
    <div className="flex h-full flex-col" style={{ maxHeight: "calc(100vh - 120px)" }}>
      <div className="mb-5 flex flex-shrink-0 items-start justify-between gap-4">
        <div>
          <h1 className="mb-1 text-[1.65rem] font-extrabold text-white">Growth Coach</h1>
          <p className="text-sm text-[#717182]">
            {llmLabel ?? "Your AI-powered strategy advisor · Available 24/7"}
          </p>
        </div>
        <button
          type="button"
          onClick={clearChat}
          disabled={loading || messages.length <= 1}
          className="flex items-center gap-1.5 rounded-lg border border-white/8 bg-white/5 px-3 py-1.5 text-xs text-[#717182] transition-all hover:border-white/15 hover:bg-white/10 hover:text-white disabled:cursor-not-allowed disabled:opacity-40"
        >
          <Trash2 size={13} />
          Clear chat
        </button>
      </div>

      <div className="scrollbar-hide mb-4 flex-1 space-y-4 overflow-y-auto">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
            {msg.role === "assistant" ? (
              <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-xl border border-violet-500/20 bg-violet-600/20">
                <Bot size={13} className="text-violet-400" />
              </div>
            ) : null}
            <div
              className={`max-w-[82%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                msg.role === "user"
                  ? "rounded-tr-sm bg-violet-600 text-white"
                  : "rounded-tl-sm border border-white/5 bg-[#0F0F1C] text-white/85"
              }`}
            >
              {msg.role === "assistant" ? (
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
              ) : (
                msg.content
              )}
            </div>
          </div>
        ))}
        {loading ? (
          <div className="flex gap-3">
            <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-xl border border-violet-500/20 bg-violet-600/20">
              <Bot size={13} className="text-violet-400" />
            </div>
            <div className="rounded-2xl rounded-tl-sm border border-white/5 bg-[#0F0F1C] px-4 py-3">
              <div className="flex items-center gap-1.5">
                {[0, 0.15, 0.3].map((d) => (
                  <div
                    key={d}
                    className="h-2 w-2 animate-bounce rounded-full bg-violet-400/50"
                    style={{ animationDelay: `${d}s` }}
                  />
                ))}
              </div>
              <p className="mt-2 text-xs text-[#717182]">
                {llmLabel?.includes("mock")
                  ? "Generating a demo response…"
                  : "Coach is thinking — first reply can take up to 60 seconds."}
              </p>
            </div>
          </div>
        ) : null}
        <div ref={messagesEndRef} />
      </div>

      <div className="flex-shrink-0 space-y-3">
        <div className="flex flex-wrap gap-2">
          {SUGGESTED_QUESTIONS.map((prompt) => (
            <button
              key={prompt}
              type="button"
              onClick={() => void send(prompt)}
              className="rounded-full bg-white/5 px-3 py-1.5 text-xs text-[#717182] transition-all hover:bg-white/10 hover:text-white"
            >
              {prompt}
            </button>
          ))}
        </div>
        <div className="flex gap-3">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                void send(input);
              }
            }}
            placeholder="Ask your growth coach anything..."
            className="flex-1 rounded-xl border border-white/8 bg-[#0F0F1C] px-4 py-3 text-sm text-white transition-all placeholder:text-[#717182] focus:border-violet-500/50 focus:outline-none"
          />
          <button
            type="button"
            onClick={() => void send(input)}
            disabled={!input.trim() || loading}
            className="flex-shrink-0 rounded-xl bg-violet-600 px-4 text-white transition-all hover:bg-violet-500 disabled:opacity-50"
          >
            <Send size={15} />
          </button>
        </div>
      </div>
    </div>
  );
}
