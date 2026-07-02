"use client";

import { useEffect, useMemo, useState } from "react";
import { Plus } from "lucide-react";

import { getActiveUserId, getCalendar, type CalendarItem } from "../../lib/api";
import { IgIcon, TtIcon, YtIcon } from "../ui/platform-icons";

const statusStyle = {
  published: "bg-emerald-500/15 text-emerald-300 border-emerald-500/20",
  scheduled: "bg-violet-500/15 text-violet-300 border-violet-500/20",
  draft: "bg-white/5 text-white/35 border-white/10",
  idea: "bg-white/5 text-white/35 border-white/10",
};

function platformIcon(platform: string | null) {
  const value = (platform ?? "").toLowerCase();
  if (value.includes("tiktok") || value === "tt") return <TtIcon size={9} />;
  if (value.includes("youtube") || value === "yt") return <YtIcon size={9} />;
  return <IgIcon size={9} />;
}

export function CalendarScreen() {
  const [selectedDay, setSelectedDay] = useState<number | null>(null);
  const [items, setItems] = useState<CalendarItem[]>([]);
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth();
  const monthLabel = now.toLocaleDateString(undefined, { month: "long", year: "numeric" });
  const days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const firstOffset = new Date(year, month, 1).getDay();
  const total = new Date(year, month + 1, 0).getDate();
  const today = now.getDate();
  const cells = Array.from({ length: firstOffset + total }, (_, i) =>
    i < firstOffset ? null : i - firstOffset + 1,
  );

  useEffect(() => {
    void getCalendar(getActiveUserId(), 100)
      .then((result) => setItems(result.items))
      .catch(() => setItems([]));
  }, []);

  const byDay = useMemo(() => {
    const map: Record<number, CalendarItem[]> = {};
    for (const item of items) {
      if (!item.scheduled_for) continue;
      const date = new Date(item.scheduled_for);
      if (date.getFullYear() !== year || date.getMonth() !== month) continue;
      const day = date.getDate();
      map[day] = [...(map[day] ?? []), item];
    }
    return map;
  }, [items, month, year]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="mb-1 text-[1.65rem] font-extrabold text-white">Content Calendar</h1>
          <p className="text-sm text-[#717182]">
            {monthLabel} · {items.length} pieces scheduled
          </p>
        </div>
        <button
          type="button"
          className="flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-2 text-sm font-semibold text-white transition-all hover:bg-violet-500"
        >
          <Plus size={14} />
          Schedule
        </button>
      </div>

      <div className="overflow-hidden rounded-2xl border border-white/5 bg-[#0F0F1C]">
        <div className="grid grid-cols-7 border-b border-white/5">
          {days.map((d) => (
            <div key={d} className="py-3 text-center text-[10px] font-bold uppercase tracking-widest text-[#717182]">
              {d}
            </div>
          ))}
        </div>
        <div className="grid grid-cols-7">
          {cells.map((day, idx) => {
            const events = day ? byDay[day] ?? [] : [];
            const isToday = day === today;
            const isSel = day === selectedDay;
            return (
              <div
                key={idx}
                onClick={() => day && setSelectedDay(day === selectedDay ? null : day)}
                className={`min-h-[88px] border-b border-r border-white/5 p-2 transition-colors ${
                  !day ? "bg-white/[0.01]" : "cursor-pointer hover:bg-white/[0.02]"
                } ${isToday ? "bg-violet-500/[0.04]" : ""} ${isSel ? "ring-1 ring-inset ring-violet-500/30" : ""}`}
              >
                {day ? (
                  <>
                    <span
                      className={`flex h-6 w-6 items-center justify-center rounded-full text-[11px] font-bold ${
                        isToday ? "bg-violet-600 text-white" : "text-[#717182]"
                      }`}
                    >
                      {day}
                    </span>
                    <div className="mt-1 space-y-1">
                      {events.map((ev) => (
                        <div
                          key={ev.id}
                          className={`flex items-center gap-0.5 rounded border px-1 py-0.5 text-[9px] leading-tight ${
                            statusStyle[ev.status as keyof typeof statusStyle] ?? statusStyle.draft
                          }`}
                        >
                          {platformIcon(ev.platform)}
                          <span className="truncate">{ev.notes ?? "Scheduled item"}</span>
                        </div>
                      ))}
                    </div>
                  </>
                ) : null}
              </div>
            );
          })}
        </div>
      </div>

      <div className="flex items-center gap-6">
        {[
          ["Published", "bg-emerald-500"],
          ["Scheduled", "bg-violet-500"],
          ["Draft", "bg-white/20"],
        ].map(([label, color]) => (
          <div key={label} className="flex items-center gap-2">
            <div className={`h-2 w-2 rounded-full ${color}`} />
            <span className="text-xs text-[#717182]">{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
