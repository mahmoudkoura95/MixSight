"use client";

import { motion } from "motion/react";

type Indicator = {
  label: string;
  source: string;
  value: number;
  range?: [number, number];
  color: string;
  phase: 1 | 2;
};

const indicators: Indicator[] = [
  { label: "Platform", source: "Meta-native", value: 41, color: "rgb(45,212,191)", phase: 1 },
  { label: "GA4", source: "Cross-platform", value: 44, color: "rgb(251,191,36)", phase: 1 },
  { label: "Modeled", source: "MMM posterior · 90% CI", value: 47, range: [42, 52], color: "rgb(167,139,250)", phase: 2 },
  { label: "Incrementality", source: "Geo holdout · 95% CI", value: 49, range: [43, 55], color: "rgb(244,114,182)", phase: 2 },
];

// Visual: each indicator gets a horizontal lane with a value marker
// (range shown as a band when present).
const MIN = 32;
const MAX = 60;

function pctOf(v: number) {
  return ((v - MIN) / (MAX - MIN)) * 100;
}

export function EvidenceColumnFour() {
  return (
    <div className="w-full bg-white/[0.025] border border-white/10 rounded-2xl p-6 shadow-2xl">
      <div className="flex items-start justify-between mb-6">
        <div>
          <p className="text-[10px] uppercase tracking-wider text-white/40 mb-1">
            Evidence column · Phase 2 expansion
          </p>
          <p className="text-white/90 font-medium">
            Four independent measurements of CPA · Meta — Halcyon US
          </p>
        </div>
        <span className="hidden sm:inline-flex text-[10px] text-purple-300/80 font-mono px-2 py-1 bg-purple-500/10 rounded">
          Phase 2 ships indicators 3 + 4
        </span>
      </div>

      <div className="space-y-3.5">
        {indicators.map((ind, i) => (
          <motion.div
            key={ind.label}
            initial={{ opacity: 0, x: -8 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.5, delay: i * 0.12 }}
          >
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: ind.color }} />
                <span className="text-xs font-medium text-white/90">{ind.label}</span>
                <span className="text-[10px] text-white/40">{ind.source}</span>
                {ind.phase === 2 && (
                  <span className="text-[9px] text-purple-300/70 bg-purple-500/10 px-1 py-0.5 rounded uppercase tracking-wider">
                    P2
                  </span>
                )}
              </div>
              <span className="text-xs font-mono text-white/85">
                ${ind.value}
                {ind.range && (
                  <span className="text-white/40 ml-1.5">
                    [{ind.range[0]}–{ind.range[1]}]
                  </span>
                )}
              </span>
            </div>
            <div className="relative h-3 rounded bg-white/[0.04] border border-white/5 overflow-hidden">
              {/* Tick marks */}
              {[35, 40, 45, 50, 55].map((t) => (
                <div
                  key={t}
                  className="absolute top-0 bottom-0 w-px bg-white/[0.06]"
                  style={{ left: `${pctOf(t)}%` }}
                />
              ))}
              {/* Range band */}
              {ind.range && (
                <motion.div
                  initial={{ scaleX: 0 }}
                  whileInView={{ scaleX: 1 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.6, delay: 0.3 + i * 0.12 }}
                  style={{
                    originX: 0,
                    left: `${pctOf(ind.range[0])}%`,
                    width: `${pctOf(ind.range[1]) - pctOf(ind.range[0])}%`,
                    backgroundColor: ind.color,
                    opacity: 0.25,
                  }}
                  className="absolute top-0 bottom-0 rounded"
                />
              )}
              {/* Point marker */}
              <motion.div
                initial={{ opacity: 0, scale: 0 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: 0.5 + i * 0.12 }}
                className="absolute top-1/2 -translate-y-1/2 w-3 h-3 rounded-full shadow-lg ring-2 ring-[#0f1e3d]"
                style={{
                  left: `calc(${pctOf(ind.value)}% - 0.375rem)`,
                  backgroundColor: ind.color,
                }}
              />
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-3 mt-6 pt-5 border-t border-white/10 text-[11px]">
        <Insight label="Cluster width" value="$8" hint="Tight" tone="ok" />
        <Insight label="Phase 1 alone says" value="On plan" hint="Avg $42.5" tone="neutral" />
        <Insight label="Phase 2 reveals" value="Modeled overstating" hint="True CPA closer to $48" tone="warn" />
      </div>
    </div>
  );
}

function Insight({ label, value, hint, tone }: { label: string; value: string; hint: string; tone: "ok" | "warn" | "neutral" }) {
  const toneText = tone === "ok" ? "text-emerald-300" : tone === "warn" ? "text-amber-300" : "text-white/85";
  return (
    <div>
      <p className="text-[9px] uppercase tracking-wider text-white/40 mb-1">{label}</p>
      <p className={`text-sm font-semibold ${toneText}`}>{value}</p>
      <p className="text-[10px] text-white/40 mt-0.5">{hint}</p>
    </div>
  );
}
