"use client";

import { motion } from "motion/react";
import { pacingRows, type PacingRow } from "../../_lib/mockData";

const statusStyle: Record<PacingRow["status"], { bg: string; text: string; dot: string; label: string }> = {
  green: { bg: "bg-emerald-500/15", text: "text-emerald-300", dot: "bg-emerald-400", label: "on plan" },
  amber: { bg: "bg-amber-500/15", text: "text-amber-300", dot: "bg-amber-400", label: "amber" },
  red: { bg: "bg-rose-500/15", text: "text-rose-300", dot: "bg-rose-400", label: "red" },
  critical: { bg: "bg-rose-600/25", text: "text-rose-200", dot: "bg-rose-500", label: "critical" },
  insufficient_data: { bg: "bg-white/5", text: "text-white/40", dot: "bg-white/30", label: "no data" },
};

function fmt(n: number, unit: string) {
  if (unit === "ROAS") return `${n.toFixed(1)}x`;
  if (unit === "CPM") return `$${n.toFixed(2)}`;
  return `$${n}`;
}

function fmtPct(p: number) {
  const sign = p > 0 ? "+" : "";
  return `${sign}${(p * 100).toFixed(1)}%`;
}

function fmtSpend(n: number) {
  return n >= 1000 ? `$${(n / 1000).toFixed(1)}K` : `$${n}`;
}

export function PacingTableMock() {
  return (
    <div className="w-full bg-white/[0.025] border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
      {/* Header strip */}
      <div className="flex items-center justify-between gap-3 px-5 py-3.5 border-b border-white/10 bg-white/[0.02]">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded bg-teal-400/20 text-teal-300 text-[10px] font-bold flex items-center justify-center">
            LS
          </div>
          <div>
            <p className="text-[10px] uppercase tracking-wider text-white/40">
              Week ending May 11, 2026
            </p>
            <p className="text-xs font-medium text-white/90">
              Lumen Studios · 2 clients · 2 markets · Net pacing +3.2%
            </p>
          </div>
        </div>
        <div className="hidden sm:flex items-center gap-1.5">
          <span className="px-2 py-0.5 rounded text-[10px] bg-rose-500/15 text-rose-300">
            1 critical
          </span>
          <span className="px-2 py-0.5 rounded text-[10px] bg-rose-500/15 text-rose-300">
            1 red
          </span>
          <span className="px-2 py-0.5 rounded text-[10px] bg-amber-500/15 text-amber-300">
            1 amber
          </span>
          <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-500/15 text-emerald-300">
            3 on plan
          </span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs min-w-[820px]">
          <thead className="bg-white/[0.025]">
            <tr className="text-[10px] uppercase tracking-wider text-white/40">
              <th className="text-left px-4 py-2.5 font-medium">Client · channel</th>
              <th className="text-left px-3 py-2.5 font-medium">Mkt</th>
              <th className="text-left px-3 py-2.5 font-medium">Product line</th>
              <th className="text-right px-3 py-2.5 font-medium">Spend</th>
              <th className="text-right px-3 py-2.5 font-medium">Δ</th>
              <th className="text-right px-3 py-2.5 font-medium">KPI</th>
              <th className="text-right px-3 py-2.5 font-medium">Δ</th>
              <th className="text-left px-3 py-2.5 font-medium">Evidence</th>
              <th className="text-center px-3 py-2.5 font-medium">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {pacingRows.map((r, i) => {
              const s = statusStyle[r.status];
              const negDrift = r.kpiUnit === "CPA" || r.kpiUnit === "CPC" || r.kpiUnit === "CPM";
              const driftBad = (negDrift && r.kpiDrift > 0) || (!negDrift && r.kpiDrift < 0);
              return (
                <motion.tr
                  key={`${r.client}-${r.channel}-${r.market}`}
                  initial={{ opacity: 0, y: 6 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-50px" }}
                  transition={{ duration: 0.35, delay: i * 0.06 }}
                  className="hover:bg-white/[0.02] transition-colors"
                >
                  <td className="px-4 py-2.5">
                    <div className="text-white/90 font-medium leading-tight">{r.channel}</div>
                    <div className="text-[10px] text-white/40 mt-0.5">{r.client}</div>
                  </td>
                  <td className="px-3 py-2.5 text-white/65">{r.market}</td>
                  <td className="px-3 py-2.5">
                    <span className="px-1.5 py-0.5 rounded bg-white/5 text-[10px] text-white/65">
                      {r.productLine}
                    </span>
                  </td>
                  <td className="px-3 py-2.5 text-right text-white/85 font-mono tabular-nums">
                    {fmtSpend(r.actualSpend)}
                  </td>
                  <td
                    className={`px-3 py-2.5 text-right font-mono tabular-nums ${
                      Math.abs(r.spendDrift) > 0.15
                        ? r.spendDrift > 0
                          ? "text-amber-300"
                          : "text-rose-300"
                        : "text-white/55"
                    }`}
                  >
                    {fmtPct(r.spendDrift)}
                  </td>
                  <td className="px-3 py-2.5 text-right text-white/85 font-mono tabular-nums">
                    {fmt(r.actual, r.kpiUnit)}
                    <span className="text-[10px] text-white/30 ml-1">{r.kpiUnit}</span>
                  </td>
                  <td
                    className={`px-3 py-2.5 text-right font-mono tabular-nums ${
                      driftBad ? "text-rose-300" : "text-emerald-300"
                    }`}
                  >
                    {fmtPct(r.kpiDrift)}
                  </td>
                  <td className="px-3 py-2.5">
                    <EvidenceRange row={r} />
                  </td>
                  <td className="px-3 py-2.5 text-center">
                    <span
                      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-medium ${s.bg} ${s.text}`}
                    >
                      <span className={`w-1.5 h-1.5 rounded-full ${s.dot}`} />
                      {s.label}
                    </span>
                  </td>
                </motion.tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="px-5 py-2.5 border-t border-white/10 bg-white/[0.015] flex items-center justify-between text-[10px] text-white/40">
        <span className="font-mono">Data current as of May 12 · 06:14 BST</span>
        <span>Click any row → evidence drilldown</span>
      </div>
    </div>
  );
}

function EvidenceRange({ row }: { row: PacingRow }) {
  const delta = Math.abs(row.modeDelta);
  const tight = delta < 0.1;
  const wide = delta > 0.25;
  // Visual range mapping: position dots within a 60px span by relative delta.
  const span = 56;
  // Center, then offset each dot by the delta magnitude.
  const aPos = 8;
  const bPos = 8 + delta * span;
  return (
    <div className="flex items-center gap-2">
      <div className="relative w-16 h-3">
        <div className="absolute inset-y-1.5 left-1 right-1 h-px bg-white/15" />
        <span
          className="absolute top-1/2 -translate-y-1/2 w-2 h-2 rounded-full bg-teal-400 ring-2 ring-[#0f1e3d]"
          style={{ left: `${aPos}px` }}
          aria-label="Mode A · Platform"
        />
        <span
          className={`absolute top-1/2 -translate-y-1/2 w-2 h-2 rounded-full ring-2 ring-[#0f1e3d] ${
            tight ? "bg-emerald-400" : wide ? "bg-rose-400" : "bg-amber-400"
          }`}
          style={{ left: `${Math.min(bPos, span)}px` }}
          aria-label="Mode B · GA4"
        />
      </div>
      <span
        className={`text-[10px] font-mono ${
          tight ? "text-emerald-300/70" : wide ? "text-rose-300" : "text-amber-300/80"
        }`}
      >
        Δ {(delta * 100).toFixed(1)}%
      </span>
    </div>
  );
}
