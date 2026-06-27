"use client";

import { motion } from "motion/react";
import Image from "next/image";

const sections = [
  { id: "header", delay: 0 },
  { id: "narrative", delay: 0.25 },
  { id: "table", delay: 0.5 },
  { id: "realloc", delay: 0.85 },
  { id: "audit", delay: 1.1 },
  { id: "footnote", delay: 1.35 },
];

const sectionDelay = (id: string) => sections.find((s) => s.id === id)?.delay ?? 0;

const fadeIn = (delay: number) => ({
  initial: { opacity: 0, y: 12 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-80px" } as const,
  transition: { duration: 0.5, delay, ease: [0.22, 1, 0.36, 1] as [number, number, number, number] },
});

export function DefenseKitAssembly() {
  return (
    <div className="relative w-full">
      <div className="absolute -inset-6 bg-gradient-to-br from-teal-500/15 via-transparent to-indigo-500/10 blur-3xl pointer-events-none" />
      <div className="relative bg-white text-slate-900 rounded-2xl shadow-[0_24px_60px_-12px_rgba(0,0,0,0.5)] overflow-hidden">
        <div className="px-7 pt-7 pb-2">
          {/* Header */}
          <motion.div {...fadeIn(sectionDelay("header"))} className="flex items-start justify-between border-b border-slate-200 pb-5">
            <div className="flex items-center gap-3">
              <div className="bg-slate-900 rounded-md px-2 py-1.5">
                <Image src="/logo.png" alt="" width={70} height={18} />
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-wider text-slate-400">
                  Weekly defense kit
                </p>
                <p className="font-semibold text-slate-900 text-sm">
                  Halcyon Apparel · Week ending May 11, 2026
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-[10px] uppercase tracking-wider text-slate-400">
                Prepared for
              </p>
              <p className="text-xs font-medium text-slate-700">Sara M. · CMO</p>
            </div>
          </motion.div>

          {/* Narrative */}
          <motion.div {...fadeIn(sectionDelay("narrative"))} className="py-5 border-b border-slate-100">
            <p className="text-[10px] uppercase tracking-wider text-teal-700 font-medium mb-2">
              Top-line summary
            </p>
            <p className="text-sm leading-relaxed text-slate-700">
              Net pacing is{" "}
              <span className="font-semibold text-slate-900">+3.2% vs. plan</span> with
              healthy efficiency on US Meta and UK Premium. Two areas need attention:{" "}
              <span className="font-semibold text-slate-900">
                US Google Search
              </span>{" "}
              is underspending against a falling ROAS, and{" "}
              <span className="font-semibold text-slate-900">
                UK TikTok
              </span>{" "}
              is over-pacing reach at +38% CPM. Recommended action below.
            </p>
            <div className="mt-3 inline-flex items-center gap-1.5 text-[10px] text-slate-400 italic">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              Narrative AI-drafted · editable · falls back to template on outage
            </div>
          </motion.div>

          {/* Pacing table excerpt */}
          <motion.div {...fadeIn(sectionDelay("table"))} className="py-5 border-b border-slate-100">
            <p className="text-[10px] uppercase tracking-wider text-slate-400 mb-3">
              Pacing — top variances
            </p>
            <div className="rounded-md border border-slate-200 overflow-hidden">
              <table className="w-full text-[11px]">
                <thead className="bg-slate-50 text-slate-500">
                  <tr>
                    <th className="text-left px-3 py-2 font-medium">Channel</th>
                    <th className="text-right px-3 py-2 font-medium">Spend Δ</th>
                    <th className="text-right px-3 py-2 font-medium">KPI Δ</th>
                    <th className="text-center px-3 py-2 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {[
                    { ch: "Halcyon US · Meta — Prospecting", s: "+5.7%", k: "+7.9% CPA", st: "on plan", tone: "ok" },
                    { ch: "Halcyon US · Google — Search", s: "−22.3%", k: "−26.2% ROAS", st: "critical", tone: "bad" },
                    { ch: "Halcyon UK · TikTok — Video", s: "+26.7%", k: "+38.2% CPM", st: "red", tone: "bad" },
                    { ch: "Stratton US · Meta — Remarketing", s: "−1.1%", k: "+3.7% ROAS", st: "on plan", tone: "ok" },
                  ].map((r) => (
                    <tr key={r.ch}>
                      <td className="px-3 py-2 text-slate-800 font-medium">{r.ch}</td>
                      <td className={`px-3 py-2 text-right font-mono ${r.tone === "bad" ? "text-rose-600" : "text-slate-600"}`}>
                        {r.s}
                      </td>
                      <td className={`px-3 py-2 text-right font-mono ${r.tone === "bad" ? "text-rose-600" : "text-emerald-600"}`}>
                        {r.k}
                      </td>
                      <td className="px-3 py-2 text-center">
                        <span
                          className={`inline-block px-1.5 py-0.5 rounded text-[10px] font-medium ${
                            r.tone === "bad" ? "bg-rose-100 text-rose-700" : "bg-emerald-100 text-emerald-700"
                          }`}
                        >
                          {r.st}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>

          {/* Reallocation */}
          <motion.div {...fadeIn(sectionDelay("realloc"))} className="py-5 border-b border-slate-100">
            <p className="text-[10px] uppercase tracking-wider text-slate-400 mb-3">
              Recommended reallocation · option 1 of 3
            </p>
            <div className="rounded-md bg-teal-50 border border-teal-200 p-4">
              <div className="flex items-center justify-between mb-2.5">
                <div className="flex items-center gap-2.5">
                  <span className="w-6 h-6 rounded-full bg-teal-600 text-white text-[11px] font-bold flex items-center justify-center">
                    1
                  </span>
                  <div>
                    <p className="text-sm font-semibold text-slate-900">
                      Halcyon UK · TikTok → Meta Prospecting
                    </p>
                    <p className="text-[10px] text-slate-500 mt-0.5">
                      within-market · same-product-line · Premium
                    </p>
                  </div>
                </div>
                <span className="text-xs font-mono text-teal-800 bg-white px-2 py-1 rounded border border-teal-200">
                  Move $4,500
                </span>
              </div>
              <div className="grid grid-cols-2 gap-3 mt-3">
                <div>
                  <p className="text-[10px] uppercase tracking-wider text-slate-500">
                    Projected impact
                  </p>
                  <p className="text-sm font-semibold text-slate-900">+92 conversions</p>
                  <p className="text-[10px] text-slate-500">[+68 to +118] · 90% CI</p>
                </div>
                <div>
                  <p className="text-[10px] uppercase tracking-wider text-slate-500">
                    Confidence
                  </p>
                  <div className="flex items-center gap-1.5 mt-1">
                    <div className="flex-1 h-1.5 bg-slate-200 rounded overflow-hidden">
                      <div className="h-full bg-teal-600 rounded" style={{ width: "82%" }} />
                    </div>
                    <span className="text-[11px] font-mono text-slate-700">High</span>
                  </div>
                </div>
              </div>
              <p className="text-[11px] text-slate-600 leading-relaxed mt-3">
                TikTok CPM +38% over 14d with flat reach growth. Meta prospecting
                CPA −6% on the same audience with audience-size headroom.
              </p>
            </div>
          </motion.div>

          {/* Plan change audit */}
          <motion.div {...fadeIn(sectionDelay("audit"))} className="py-5 border-b border-slate-100">
            <p className="text-[10px] uppercase tracking-wider text-slate-400 mb-3">
              Plan changes this period
            </p>
            <ul className="space-y-1.5 text-[11px] text-slate-600">
              <li className="flex gap-2">
                <span className="text-slate-400 w-12 flex-shrink-0 font-mono">Apr 14</span>
                <span>+$8K Meta · −$8K Google (client request)</span>
              </li>
              <li className="flex gap-2">
                <span className="text-slate-400 w-12 flex-shrink-0 font-mono">Apr 24</span>
                <span>UK TikTok line launched · $15K (Premium)</span>
              </li>
              <li className="flex gap-2">
                <span className="text-slate-400 w-12 flex-shrink-0 font-mono">May 06</span>
                <span>US PMax cap reduced to $35K (efficiency goal)</span>
              </li>
            </ul>
          </motion.div>

          {/* Footnote */}
          <motion.div {...fadeIn(sectionDelay("footnote"))} className="pt-4 pb-5">
            <p className="text-[10px] text-slate-400 italic leading-relaxed">
              Methodology · Mode A: platform-native (Meta, Google, TikTok). Mode B:
              GA4 data-driven attribution. Reconciliation factors updated weekly.
              Confidence intervals derived from rolling 14-day stability heuristics
              (Phase 1) and MMM posteriors (Phase 2+). Generated by MixSight ·{" "}
              <span className="not-italic font-mono">v0.1 · pre-release</span>
            </p>
          </motion.div>
        </div>

        {/* Toolbar */}
        <div className="bg-slate-50 border-t border-slate-200 px-7 py-3 flex items-center justify-between text-[10px] text-slate-500">
          <span>Defense kit · 1 of 1</span>
          <span className="flex items-center gap-3">
            <span className="px-2 py-0.5 bg-white border border-slate-200 rounded font-mono">
              Edit narrative
            </span>
            <span className="px-2 py-0.5 bg-teal-600 text-white rounded font-mono">
              Download PDF
            </span>
          </span>
        </div>
      </div>
    </div>
  );
}
