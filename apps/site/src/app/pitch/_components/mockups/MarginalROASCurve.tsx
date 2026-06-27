"use client";

import { motion } from "motion/react";
import { marginalROASCurve } from "../../_lib/mockData";

// Saturation curve: y = ROAS, x = spend. Visualize current spend marker,
// shaded "above-current" projection arrow.
const W = 420;
const H = 200;
const PAD = { l: 36, r: 16, t: 16, b: 28 };

function projX(spend: number, max: number) {
  return PAD.l + (spend / max) * (W - PAD.l - PAD.r);
}
function projY(roas: number, max: number) {
  return PAD.t + (1 - roas / max) * (H - PAD.t - PAD.b);
}

export function MarginalROASCurve() {
  const data = marginalROASCurve;
  const maxSpend = data.points[data.points.length - 1].spend;
  const maxROAS = 6;

  const path = data.points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${projX(p.spend, maxSpend).toFixed(1)} ${projY(p.roas, maxROAS).toFixed(1)}`)
    .join(" ");

  const fillPath = `${path} L ${projX(maxSpend, maxSpend)} ${projY(0, maxROAS)} L ${projX(0, maxSpend)} ${projY(0, maxROAS)} Z`;

  const currentX = projX(data.current, maxSpend);
  const currentROAS = data.points.find((p) => p.spend === data.current)?.roas ?? 0;
  const currentY = projY(currentROAS, maxROAS);

  // Marginal projection: at +$30K, ROAS = 2.9
  const projSpend = data.current + 30;
  const projROAS = 2.9;
  const projXEnd = projX(projSpend, maxSpend);
  const projYEnd = projY(projROAS, maxROAS);

  return (
    <div className="w-full bg-white/[0.025] border border-white/10 rounded-2xl p-6 shadow-2xl">
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-[10px] uppercase tracking-wider text-white/40 mb-1">
            {data.channel}
          </p>
          <p className="text-white/90 font-medium">Marginal ROAS curve · MMM posterior</p>
        </div>
        <span className="text-[10px] text-purple-300/80 font-mono px-2 py-1 bg-purple-500/10 rounded">
          Phase 2
        </span>
      </div>

      <div className="rounded-lg bg-[#0a162e]/60 border border-white/5 p-3">
        <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto">
          <defs>
            <linearGradient id="roas-fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="rgba(167,139,250,0.25)" />
              <stop offset="100%" stopColor="rgba(167,139,250,0)" />
            </linearGradient>
          </defs>

          {/* Grid */}
          {[1, 2, 3, 4, 5].map((y) => (
            <g key={y}>
              <line
                x1={PAD.l}
                x2={W - PAD.r}
                y1={projY(y, maxROAS)}
                y2={projY(y, maxROAS)}
                stroke="rgba(255,255,255,0.05)"
              />
              <text
                x={PAD.l - 6}
                y={projY(y, maxROAS) + 3}
                textAnchor="end"
                fill="rgba(255,255,255,0.3)"
                fontSize="9"
              >
                {y}x
              </text>
            </g>
          ))}

          {/* Fill */}
          <motion.path
            d={fillPath}
            fill="url(#roas-fill)"
            initial={{ pathLength: 0, opacity: 0 }}
            whileInView={{ pathLength: 1, opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1.5 }}
          />

          {/* Curve */}
          <motion.path
            d={path}
            stroke="rgb(167,139,250)"
            strokeWidth="2.5"
            fill="none"
            initial={{ pathLength: 0 }}
            whileInView={{ pathLength: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 1.5, ease: "easeOut" }}
          />

          {/* Current spend marker */}
          <motion.line
            x1={currentX}
            x2={currentX}
            y1={PAD.t}
            y2={H - PAD.b}
            stroke="rgba(45,212,191,0.5)"
            strokeWidth="1"
            strokeDasharray="3 3"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 1.2, duration: 0.4 }}
          />
          <motion.circle
            cx={currentX}
            cy={currentY}
            r="5"
            fill="rgb(45,212,191)"
            stroke="rgb(15,30,61)"
            strokeWidth="2"
            initial={{ opacity: 0, scale: 0 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 1.3 }}
          />

          {/* Marginal projection point */}
          <motion.circle
            cx={projXEnd}
            cy={projYEnd}
            r="4"
            fill="rgb(251,113,133)"
            stroke="rgb(15,30,61)"
            strokeWidth="2"
            initial={{ opacity: 0, scale: 0 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 1.6 }}
          />
          {/* Arrow from current to projected */}
          <motion.line
            x1={currentX}
            x2={projXEnd}
            y1={currentY}
            y2={projYEnd}
            stroke="rgb(251,113,133)"
            strokeWidth="1.5"
            strokeDasharray="4 3"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 1.7 }}
          />

          {/* X axis labels */}
          {[0, 40, 80, 120, 150].map((s) => (
            <text
              key={s}
              x={projX(s, maxSpend)}
              y={H - PAD.b + 14}
              textAnchor="middle"
              fill="rgba(255,255,255,0.3)"
              fontSize="9"
            >
              ${s}K
            </text>
          ))}
        </svg>
      </div>

      <div className="grid grid-cols-3 gap-3 mt-5">
        <Stat label="Current spend" value="$90K" hint="ROAS 3.5x" color="teal" />
        <Stat label="Marginal +$30K" value="ROAS 2.9x" hint="−0.6x at margin" color="rose" />
        <Stat label="Decision" value="Hold spend" hint="Diminishing returns" color="white" />
      </div>
    </div>
  );
}

function Stat({ label, value, hint, color }: { label: string; value: string; hint: string; color: "teal" | "rose" | "white" }) {
  const cls = color === "teal" ? "text-teal-300" : color === "rose" ? "text-rose-300" : "text-white";
  return (
    <div className="rounded-lg bg-white/[0.025] border border-white/10 p-3">
      <p className="text-[10px] uppercase tracking-wider text-white/40">{label}</p>
      <p className={`text-base font-semibold mt-0.5 ${cls}`}>{value}</p>
      <p className="text-[10px] text-white/40 mt-0.5">{hint}</p>
    </div>
  );
}
