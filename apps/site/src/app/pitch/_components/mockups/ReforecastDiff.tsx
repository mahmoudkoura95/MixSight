"use client";

import { motion } from "motion/react";
import { forecastChart } from "../../_lib/mockData";
import { AlertCircle } from "lucide-react";

const W = 420;
const H = 200;
const PAD = { l: 36, r: 16, t: 14, b: 26 };

function projX(week: number, max: number) {
  return PAD.l + ((week - 1) / (max - 1)) * (W - PAD.l - PAD.r);
}
function projY(v: number, min: number, max: number) {
  return PAD.t + (1 - (v - min) / (max - min)) * (H - PAD.t - PAD.b);
}

export function ReforecastDiff() {
  const data = forecastChart;
  const min = 25;
  const max = 60;
  const maxWeek = data.trajectory.length;

  const baselinePath = data.trajectory
    .map((p, i) => `${i === 0 ? "M" : "L"} ${projX(p.week, maxWeek).toFixed(1)} ${projY(p.baseline, min, max).toFixed(1)}`)
    .join(" ");

  const reforecastPath = data.trajectory
    .map((p, i) => `${i === 0 ? "M" : "L"} ${projX(p.week, maxWeek).toFixed(1)} ${projY(p.reforecast, min, max).toFixed(1)}`)
    .join(" ");

  // Divergence point: week 3 (where reforecast departs)
  const diverge = data.trajectory[2];
  const divergeX = projX(diverge.week, maxWeek);
  const divergeY = projY(diverge.baseline, min, max);

  return (
    <div className="w-full bg-white/[0.025] border border-white/10 rounded-2xl p-6 shadow-2xl">
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-[10px] uppercase tracking-wider text-white/40 mb-1">
            Reforecast · triggered by competitor announcement
          </p>
          <p className="text-white/90 font-medium">
            May 12 reforecast vs. May 05 baseline
          </p>
        </div>
        <span className="text-[10px] text-indigo-300/80 font-mono px-2 py-1 bg-indigo-500/10 rounded">
          Phase 3c
        </span>
      </div>

      <div className="rounded-lg bg-[#0a162e]/60 border border-white/5 p-3">
        <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto">
          {/* Grid */}
          {[30, 40, 50].map((y) => (
            <line
              key={y}
              x1={PAD.l}
              x2={W - PAD.r}
              y1={projY(y, min, max)}
              y2={projY(y, min, max)}
              stroke="rgba(255,255,255,0.05)"
            />
          ))}

          {/* Baseline (faded) */}
          <motion.path
            d={baselinePath}
            stroke="rgb(45,212,191)"
            strokeOpacity="0.5"
            strokeWidth="1.5"
            fill="none"
            strokeDasharray="4 3"
            initial={{ pathLength: 0 }}
            whileInView={{ pathLength: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1.2 }}
          />

          {/* Reforecast (solid) */}
          <motion.path
            d={reforecastPath}
            stroke="rgb(251,113,133)"
            strokeWidth="2"
            fill="none"
            initial={{ pathLength: 0 }}
            whileInView={{ pathLength: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1.4, delay: 0.3, ease: "easeOut" }}
          />

          {/* Divergence annotation */}
          <motion.circle
            cx={divergeX}
            cy={divergeY}
            r="5"
            fill="rgb(251,191,36)"
            stroke="rgb(15,30,61)"
            strokeWidth="2"
            initial={{ opacity: 0, scale: 0 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 1.5 }}
          />
          <motion.line
            x1={divergeX}
            y1={divergeY}
            x2={divergeX + 60}
            y2={divergeY - 40}
            stroke="rgba(251,191,36,0.4)"
            strokeWidth="1"
            initial={{ pathLength: 0 }}
            whileInView={{ pathLength: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 1.7, duration: 0.4 }}
          />
          <motion.text
            x={divergeX + 64}
            y={divergeY - 40}
            fill="rgba(251,191,36,0.9)"
            fontSize="10"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 1.9 }}
          >
            Divergence
          </motion.text>

          {/* X labels */}
          {data.trajectory.map((p) => (
            <text key={p.week} x={projX(p.week, maxWeek)} y={H - PAD.b + 14} textAnchor="middle" fill="rgba(255,255,255,0.3)" fontSize="9">
              W{p.week}
            </text>
          ))}
        </svg>
      </div>

      <div className="mt-4 flex items-center gap-3 text-[11px]">
        <span className="inline-flex items-center gap-2 text-white/55">
          <span className="w-3 h-0.5 bg-teal-400/50 inline-block" />
          May 05 baseline
        </span>
        <span className="inline-flex items-center gap-2 text-white/55">
          <span className="w-3 h-0.5 bg-rose-400 inline-block" />
          May 12 reforecast
        </span>
      </div>

      <div className="mt-4 px-4 py-3 rounded-lg bg-amber-500/5 border border-amber-500/20 flex items-start gap-3">
        <AlertCircle className="w-4 h-4 text-amber-300 mt-0.5 flex-shrink-0" aria-hidden />
        <div className="text-[11px] text-white/70 leading-relaxed">
          <span className="font-semibold text-amber-200">Reforecast trigger · May 12 09:32 BST.</span>{" "}
          Detected: competitor Allium Skin announced product launch May 11. Google
          Trends &quot;premium skin care&quot; +180% over 5d. Weeks 5–8 contribution
          projection lowered by ~$28K assuming current spend. Decision: hold spend
          or reallocate $8K from Premium to Core?
        </div>
      </div>
    </div>
  );
}
