"use client";

import { motion } from "motion/react";

const days = Array.from({ length: 30 }, (_, i) => i + 1);

type EventCell = { day: number; span: number; label: string; tone: "promo" | "holiday"; lift?: string };
const events: EventCell[] = [
  { day: 5, span: 3, label: "Memorial Day promo", tone: "promo", lift: "1.6x lift" },
  { day: 12, span: 1, label: "Brand drop", tone: "promo", lift: "1.3x lift" },
  { day: 20, span: 4, label: "Loyalty event", tone: "promo", lift: "1.8x lift" },
  { day: 27, span: 2, label: "Public holiday (UK)", tone: "holiday" },
];

export function PromotionalCalendar() {
  // Build a map of day → event for quick lookup
  const eventMap = new Map<number, { event: EventCell; isStart: boolean }>();
  events.forEach((e) => {
    for (let i = 0; i < e.span; i++) {
      eventMap.set(e.day + i, { event: e, isStart: i === 0 });
    }
  });

  return (
    <div className="w-full bg-white/[0.025] border border-white/10 rounded-2xl p-6 shadow-2xl">
      <div className="flex items-center justify-between mb-5">
        <div>
          <p className="text-[10px] uppercase tracking-wider text-white/40 mb-1">
            Promotional calendar · May 2026
          </p>
          <p className="text-white/90 font-medium">
            AM-entered events · fed to the MMM as known shocks
          </p>
        </div>
        <span className="text-[10px] text-purple-300/80 font-mono px-2 py-1 bg-purple-500/10 rounded">
          Phase 2a
        </span>
      </div>

      {/* Calendar grid: 6 weeks x 7 days. Start day approximated; just lay 30 days in a 5x7 grid. */}
      <div className="rounded-lg bg-[#0a162e]/60 border border-white/5 p-3">
        <div className="grid grid-cols-7 gap-1.5 text-[10px] text-white/40 mb-2 px-1">
          {["S", "M", "T", "W", "T", "F", "S"].map((d, i) => (
            <span key={i} className="text-center">{d}</span>
          ))}
        </div>
        <div className="grid grid-cols-7 gap-1.5">
          {days.map((d, idx) => {
            const entry = eventMap.get(d);
            const isPromo = entry?.event.tone === "promo";
            const isHoliday = entry?.event.tone === "holiday";
            return (
              <motion.div
                key={d}
                initial={{ opacity: 0, scale: 0.85 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ duration: 0.3, delay: idx * 0.012 }}
                className={`relative h-14 rounded-md border flex flex-col items-start justify-start p-1.5 text-[10px] ${
                  isPromo
                    ? "border-teal-400/50 bg-teal-500/10"
                    : isHoliday
                      ? "border-amber-400/40 bg-amber-500/10"
                      : "border-white/5 bg-white/[0.02]"
                }`}
              >
                <span className={isPromo || isHoliday ? "text-white/85 font-medium" : "text-white/45"}>
                  {d}
                </span>
                {entry?.isStart && (
                  <span className={`text-[9px] mt-0.5 leading-tight ${isPromo ? "text-teal-200" : "text-amber-200"}`}>
                    {entry.event.label}
                  </span>
                )}
                {entry?.isStart && entry.event.lift && (
                  <span className="absolute bottom-1 right-1 text-[8px] font-mono text-teal-300/80">
                    {entry.event.lift}
                  </span>
                )}
              </motion.div>
            );
          })}
        </div>
      </div>

      <div className="mt-4 flex flex-wrap gap-2 text-[10px]">
        <Tag color="teal" label="Promo" />
        <Tag color="amber" label="Holiday" />
        <Tag color="purple" label="Adstock · Hill · Fourier · Trends" />
      </div>
    </div>
  );
}

function Tag({ color, label }: { color: "teal" | "amber" | "purple"; label: string }) {
  const map = {
    teal: "border-teal-400/30 text-teal-200 bg-teal-500/5",
    amber: "border-amber-400/30 text-amber-200 bg-amber-500/5",
    purple: "border-purple-400/30 text-purple-200 bg-purple-500/5",
  } as const;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded border ${map[color]}`}>
      <span className="w-1.5 h-1.5 rounded-full" style={{
        backgroundColor: color === "teal" ? "rgb(45,212,191)" : color === "amber" ? "rgb(251,191,36)" : "rgb(167,139,250)"
      }} />
      {label}
    </span>
  );
}
