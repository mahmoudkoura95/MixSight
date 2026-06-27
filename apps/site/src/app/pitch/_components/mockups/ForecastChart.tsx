"use client";

import { motion } from "motion/react";
import { forecastChart } from "../../_lib/mockData";

const W = 420;
const H = 200;
const PAD = { l: 36, r: 16, t: 14, b: 26 };

function projX(week: number, max: number) {
  return PAD.l + ((week - 1) / (max - 1)) * (W - PAD.l - PAD.r);
}
function projY(v: number, min: number, max: number) {
  return PAD.t + (1 - (v - min) / (max - min)) * (H - PAD.t - PAD.b);
}

export function ForecastChart() {
  const data = forecastChart;
  const min = 25;
  const max = 60;
  const maxWeek = data.trajectory.length;

  // Build baseline line + ribbon
  const linePath = data.trajectory
    .map((p, i) => `${i === 0 ? "M" : "L"} ${projX(p.week, maxWeek).toFixed(1)} ${projY(p.baseline, min, max).toFixed(1)}`)
    .join(" ");

  const hiPath = data.trajectory
    .map((p, i) => `${i === 0 ? "M" : "L"} ${projX(p.week, maxWeek).toFixed(1)} ${projY(p.hi, min, max).toFixed(1)}`)
    .join(" ");

  const loReversePath = [...data.trajectory].reverse()
    .map((p, i) => `${i === 0 ? "L" : "L"} ${projX(p.week, maxWeek).toFixed(1)} ${projY(p.lo, min, max).toFixed(1)}`)
    .join(" ");

  const ribbon = `${hiPath} ${loReversePath} Z`;

  return (
    <div className="w-full bg-white/[0.025] border border-white/10 rounded-2xl p-6 shadow-2xl">
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-[10px] uppercase tracking-wider text-white/40 mb-1">
            8-week forecast · {data.channel}
          </p>
          <p className="text-white/90 font-medium">{data.unit} · 90% credible interval</p>
        </div>
        <span className="text-[10px] text-indigo-300/80 font-mono px-2 py-1 bg-indigo-500/10 rounded">
          Phase 3
        </span>
      </div>

      <div className="rounded-lg bg-[#0a162e]/60 border border-white/5 p-3">
        <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto">
          <defs>
            <linearGradient id="ribbon-fade" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="rgba(45,212,191,0.25)" />
              <stop offset="100%" stopColor="rgba(45,212,191,0.1)" />
            </linearGradient>
          </defs>

          {/* Grid */}
          {[30, 40, 50].map((y) => (
            <g key={y}>
              <line
                x1={PAD.l}
                x2={W - PAD.r}
                y1={projY(y, min, max)}
                y2={projY(y, min, max)}
                stroke="rgba(255,255,255,0.05)"
              />
              <text x={PAD.l - 6} y={projY(y, min, max) + 3} textAnchor="end" fill="rgba(255,255,255,0.3)" fontSize="9">
                {y}
              </text>
            </g>
          ))}

          {/* Ribbon */}
          <motion.path
            d={ribbon}
            fill="url(#ribbon-fade)"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1.2, delay: 0.3 }}
          />

          {/* Baseline */}
          <motion.path
            d={linePath}
            stroke="rgb(45,212,191)"
            strokeWidth="2"
            fill="none"
            initial={{ pathLength: 0 }}
            whileInView={{ pathLength: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1.4, ease: "easeOut" }}
          />

          {/* Dots */}
          {data.trajectory.map((p, i) => (
            <motion.circle
              key={p.week}
              cx={projX(p.week, maxWeek)}
              cy={projY(p.baseline, min, max)}
              r="3"
              fill="rgb(45,212,191)"
              stroke="rgb(15,30,61)"
              strokeWidth="1.5"
              initial={{ opacity: 0, scale: 0 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 + i * 0.08 }}
            />
          ))}

          {/* x axis labels */}
          {data.trajectory.map((p) => (
            <text
              key={p.week}
              x={projX(p.week, maxWeek)}
              y={H - PAD.b + 14}
              textAnchor="middle"
              fill="rgba(255,255,255,0.3)"
              fontSize="9"
            >
              W{p.week}
            </text>
          ))}
        </svg>
      </div>

      <div className="grid grid-cols-3 gap-3 mt-5 text-[11px]">
        <Stat label="Week 8 forecast" value="49K conv" hint="[40–58K] · 90% CI" />
        <Stat label="vs. Week 1" value="+29%" hint="Trajectory rising" />
        <Stat label="Confidence" value="Stable" hint="Backtest within band" tone="ok" />
      </div>
    </div>
  );
}

function Stat({ label, value, hint, tone }: { label: string; value: string; hint: string; tone?: "ok" }) {
  return (
    <div className="rounded-lg bg-white/[0.025] border border-white/10 p-3">
      <p className="text-[10px] uppercase tracking-wider text-white/40">{label}</p>
      <p className={`text-base font-semibold mt-0.5 ${tone === "ok" ? "text-emerald-300" : "text-white"}`}>
        {value}
      </p>
      <p className="text-[10px] text-white/40 mt-0.5">{hint}</p>
    </div>
  );
}
