"use client";

import { motion } from "motion/react";

// Three small charts: trace plot, posterior predictive, residuals.
const traceLines = [
  [0.5, 0.6, 0.55, 0.62, 0.58, 0.6, 0.59, 0.61, 0.6, 0.6],
  [0.62, 0.58, 0.61, 0.59, 0.6, 0.61, 0.6, 0.59, 0.61, 0.6],
  [0.55, 0.59, 0.6, 0.6, 0.61, 0.59, 0.6, 0.6, 0.6, 0.6],
];

const ppcSamples = [
  { x: 0.55, y: 0.4 },
  { x: 0.58, y: 0.75 },
  { x: 0.6, y: 1.0 },
  { x: 0.62, y: 0.7 },
  { x: 0.64, y: 0.35 },
  { x: 0.66, y: 0.15 },
  { x: 0.68, y: 0.06 },
];

const residuals = Array.from({ length: 18 }, (_, i) => ({
  week: i,
  val: ((i % 5) - 2) * 0.15 + (Math.sin(i) * 0.1),
}));

function plotLine(values: number[], w: number, h: number) {
  const min = 0.5;
  const max = 0.7;
  const stepX = w / (values.length - 1);
  return values
    .map((v, i) => `${i === 0 ? "M" : "L"} ${(i * stepX).toFixed(1)} ${(h - ((v - min) / (max - min)) * h).toFixed(1)}`)
    .join(" ");
}

export function MMMDiagnosticsPanel() {
  return (
    <div className="w-full bg-white/[0.025] border border-white/10 rounded-2xl p-6 shadow-2xl">
      <div className="flex items-center justify-between mb-5">
        <div>
          <p className="text-[10px] uppercase tracking-wider text-white/40 mb-1">
            Model diagnostics · weekly refit
          </p>
          <p className="text-white/90 font-medium">Bayesian MMM · Halcyon US channels</p>
        </div>
        <span className="hidden sm:inline-flex items-center gap-1.5 text-[10px] text-emerald-300 bg-emerald-500/10 px-2 py-1 rounded">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          Stable · credible for forecasting
        </span>
      </div>

      <div className="grid sm:grid-cols-3 gap-3">
        {/* Trace plot */}
        <DiagCard title="Trace plot" hint="4 chains · convergence">
          <svg viewBox="0 0 140 60" className="w-full h-auto">
            {traceLines.map((line, i) => (
              <motion.path
                key={i}
                d={plotLine(line, 140, 60)}
                stroke={["rgb(45,212,191)", "rgb(167,139,250)", "rgb(251,191,36)"][i]}
                strokeWidth="1"
                fill="none"
                opacity={0.8}
                initial={{ pathLength: 0 }}
                whileInView={{ pathLength: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 1.1, delay: i * 0.15 }}
              />
            ))}
          </svg>
        </DiagCard>

        {/* Posterior predictive */}
        <DiagCard title="Posterior predictive" hint="Samples vs. actual">
          <svg viewBox="0 0 140 60" className="w-full h-auto">
            <line x1="0" y1="55" x2="140" y2="55" stroke="rgba(255,255,255,0.1)" />
            {ppcSamples.map((s, i) => (
              <motion.rect
                key={i}
                x={i * 18 + 6}
                width={14}
                y={55 - s.y * 48}
                height={s.y * 48}
                fill="rgb(167,139,250)"
                opacity={0.7}
                initial={{ scaleY: 0 }}
                whileInView={{ scaleY: 1 }}
                viewport={{ once: true }}
                style={{ transformOrigin: "0% 100%", transformBox: "fill-box" }}
                transition={{ duration: 0.5, delay: i * 0.06 }}
              />
            ))}
            {/* Actual = dashed vertical */}
            <line x1="62" y1="6" x2="62" y2="55" stroke="rgb(45,212,191)" strokeWidth="1.5" strokeDasharray="3 2" />
          </svg>
        </DiagCard>

        {/* Residuals */}
        <DiagCard title="Residuals" hint="No autocorrelation">
          <svg viewBox="0 0 140 60" className="w-full h-auto">
            <line x1="0" y1="30" x2="140" y2="30" stroke="rgba(255,255,255,0.15)" />
            {residuals.map((r, i) => (
              <motion.circle
                key={i}
                cx={(i / (residuals.length - 1)) * 132 + 4}
                cy={30 - r.val * 40}
                r="1.6"
                fill={Math.abs(r.val) > 0.2 ? "rgb(251,191,36)" : "rgb(45,212,191)"}
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 0.85 }}
                viewport={{ once: true }}
                transition={{ delay: 0.4 + i * 0.03 }}
              />
            ))}
          </svg>
        </DiagCard>
      </div>

      <div className="mt-5 grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
        <Pill k="R̂" v="< 1.01" tone="ok" />
        <Pill k="ESS" v="> 1,200" tone="ok" />
        <Pill k="CI width" v="±$4" tone="ok" />
        <Pill k="Refit" v="42 min" tone="neutral" />
      </div>
    </div>
  );
}

function DiagCard({ title, hint, children }: { title: string; hint: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg bg-[#0a162e]/60 border border-white/5 p-3">
      <div className="flex items-center justify-between mb-2">
        <p className="text-[10px] text-white/65 font-medium">{title}</p>
        <p className="text-[9px] text-white/30">{hint}</p>
      </div>
      {children}
    </div>
  );
}

function Pill({ k, v, tone }: { k: string; v: string; tone: "ok" | "neutral" }) {
  const toneCls = tone === "ok" ? "text-emerald-300" : "text-white/80";
  return (
    <div className="flex items-center justify-between px-2.5 py-1.5 rounded bg-white/[0.025] border border-white/5">
      <span className="text-white/45 font-mono">{k}</span>
      <span className={`font-mono ${toneCls}`}>{v}</span>
    </div>
  );
}
