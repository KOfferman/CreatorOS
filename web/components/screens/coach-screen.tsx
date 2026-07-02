"use client";

import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Bot, Send } from "lucide-react";

import { askCoach, getActiveUserId } from "../../lib/api";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: string;
};

const HISTORY_KEY = "creatoros.coach.history.v1";
const SUGGESTED_QUESTIONS = [
  "Why is my reach dropping?",
  "Best posting times for my audience",
  "How to improve my hook rate",
  "Content pillars for my niche",
];

function newMessage(role: "user" | "assistant", content: string): Message {
  return {
    id: crypto.randomUUID(),
    role,
    content,
    createdAt: new Date().toISOString(),
  };
}

export function CoachScreen() {
  const [messages, setMessages] = useState<Message[]>(() => {
    if (typeof window === "undefined") return [];
    try {
      const raw = window.localStorage.getItem(HISTORY_KEY);
      if (!raw) {
        return [
          newMessage(
            "assistant",
            "Hey! 👋 I've analyzed your recent content signals. Ready to push your growth even higher?",
          ),
        ];
      }
      const parsed = JSON.parse(raw) as Message[];
      return Array.isArray(parsed) && parsed.length ? parsed : [];
    } catch {
      return [];
    }
  });
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(messages));
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
      const response = await askCoach({ user_id: getActiveUserId(), question: text });
      const body = [
        response.direct_coaching_response,
        response.recommended_next_actions.length
          ? `\n\n**Next actions:**\n${response.recommended_next_actions.map((a) => `- ${a}`).join("\n")}`
          : "",
        response.risk_warning ? `\n\n⚠️ ${response.risk_warning}` : "",
      ].join("");
      setMessages((m) => [...m, newMessage("assistant", body)]);
    } catch {
      setMessages((m) => [
        ...m,
        newMessage("assistant", "I couldn't reach the coach service. Please verify the API is running."),
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full flex-col" style={{ maxHeight: "calc(100vh - 120px)" }}>
      <div className="mb-5 flex-shrink-0">
        <h1 className="mb-1 text-[1.65rem] font-extrabold text-white">Growth Coach</h1>
        <p className="text-sm text-[#717182]">Your AI-powered strategy advisor · Available 24/7</p>
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
