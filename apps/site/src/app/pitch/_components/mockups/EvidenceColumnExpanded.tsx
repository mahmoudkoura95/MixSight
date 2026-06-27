"use client";

import { motion } from "motion/react";

// Two efficiency curves over 12 weeks, with reconciliation factor + footnote.
const weeks = Array.from({ length: 12 }, (_, i) => i);
// Mode A (Meta platform-native) — generally healthier
const seriesA = [42, 40, 41, 39, 40, 38, 39, 37, 38, 39, 41, 40];
// Mode B (GA4 cross-platform) — slightly worse, slightly noisier
const seriesB = [46, 47, 44, 45, 43, 44, 45, 41, 43, 46, 47, 44];

function pathFor(series: number[], width: number, height: number, min: number, max: number) {
  const stepX = width / (series.length - 1);
  return series
    .map((v, i) => {
      const x = i * stepX;
      const y = height - ((v - min) / (max - min)) * height;
      return `${i === 0 ? "M" : "L"} ${x.toFixed(1)} ${y.toFixed(1)}`;
    })
    .join(" ");
}

export function EvidenceColumnExpanded() {
  const min = 32;
  const max = 50;
  const w = 360;
  const h = 120;
  const pa = pathFor(seriesA, w, h, min, max);
  const pb = pathFor(seriesB, w, h, min, max);

  return (
    <div className="w-full bg-white/[0.025] border border-white/10 rounded-2xl p-6 shadow-2xl">
      <div className="flex items-start justify-between mb-5">
        <div>
          <p className="text-[10px] uppercase tracking-wider text-white/40 mb-1">
            Evidence drilldown · Meta — Prospecting · Halcyon US · Core
          </p>
          <p className="text-white/90 font-medium">Cost per acquisition · 12 weeks</p>
        </div>
        <div className="hidden sm:flex items-center gap-3 text-[10px]">
          <span className="inline-flex items-center gap-1.5 text-teal-300">
            <span className="w-2 h-2 rounded-full bg-teal-400" />
            Platform
          </span>
          <span className="inline-flex items-center gap-1.5 text-amber-300">
            <span className="w-2 h-2 rounded-full bg-amber-400" />
            GA4
          </span>
        </div>
      </div>

      <div className="rounded-lg bg-[#0a162e]/60 border border-white/5 p-4">
        <svg viewBox={`0 0 ${w} ${h + 24}`} className="w-full h-auto">
          {/* y-axis grid */}
          {[0.25, 0.5, 0.75].map((t) => (
            <line
              key={t}
              x1="0"
              x2={w}
              y1={h * t}
              y2={h * t}
              stroke="rgba(255,255,255,0.06)"
            />
          ))}
          {/* Series A */}
          <motion.path
            d={pa}
            stroke="rgb(45,212,191)"
            strokeWidth="2"
            fill="none"
            initial={{ pathLength: 0 }}
            whileInView={{ pathLength: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1.4, ease: "easeOut" }}
          />
          {/* Series B */}
          <motion.path
            d={pb}
            stroke="rgb(251,191,36)"
            strokeWidth="2"
            fill="none"
            strokeDasharray="3 3"
            initial={{ pathLength: 0 }}
            whileInView={{ pathLength: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1.4, delay: 0.2, ease: "easeOut" }}
          />
          {/* Marker last A */}
          <motion.circle
            cx={(w / (seriesA.length - 1)) * (seriesA.length - 1)}
            cy={h - ((seriesA[seriesA.length - 1] - min) / (max - min)) * h}
            r="3"
            fill="rgb(45,212,191)"
            initial={{ opacity: 0, scale: 0 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 1.4 }}
          />
          {/* x ticks */}
          {weeks.map((wk) => (
            <text
              key={wk}
              x={(w / (seriesA.length - 1)) * wk}
              y={h + 16}
              textAnchor="middle"
              fill="rgba(255,255,255,0.3)"
              fontSize="9"
            >
              W{wk + 1}
            </text>
          ))}
        </svg>
      </div>

      <div className="grid grid-cols-3 gap-3 mt-5">
        <Stat label="Reconciliation factor" value="0.93x" hint="GA4 → Platform" />
        <Stat label="Sample size" value="3,142 conv" hint="Trailing 28d" />
        <Stat label="Delta" value="Δ 7.3%" hint="Within tolerance" tone="warn" />
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ delay: 0.6 }}
        className="mt-5 px-4 py-3 rounded-lg bg-white/[0.025] border border-white/10 text-[11px] text-white/55 leading-relaxed"
      >
        <span className="font-semibold text-white/80">Methodology · </span>
        Mode A reports Meta&apos;s last-click attribution within its own conversion window
        (7d click + 1d view). Mode B reports GA4 data-driven attribution
        cross-platform. Reconciliation factor measured weekly against incrementality
        baselines. See client-level configuration for attribution settings.
      </motion.div>
    </div>
  );
}

function Stat({ label, value, hint, tone }: { label: string; value: string; hint: string; tone?: "warn" }) {
  return (
    <div className="rounded-lg bg-white/[0.025] border border-white/10 p-3">
      <p className="text-[10px] uppercase tracking-wider text-white/40">{label}</p>
      <p
        className={`text-lg font-semibold mt-0.5 ${
          tone === "warn" ? "text-amber-300" : "text-white"
        }`}
      >
        {value}
      </p>
      <p className="text-[10px] text-white/40 mt-0.5">{hint}</p>
    </div>
  );
}
