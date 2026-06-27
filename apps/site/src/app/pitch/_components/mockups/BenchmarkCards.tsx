"use client";

import { motion } from "motion/react";
import { benchmarkCards } from "../../_lib/mockData";

function pillCls(p: number) {
  if (p >= 75) return "text-emerald-300 bg-emerald-500/10";
  if (p >= 50) return "text-teal-300 bg-teal-500/10";
  if (p >= 25) return "text-amber-300 bg-amber-500/10";
  return "text-rose-300 bg-rose-500/10";
}

export function BenchmarkCards() {
  return (
    <div className="w-full bg-white/[0.025] border border-white/10 rounded-2xl p-6 shadow-2xl">
      <div className="flex items-center justify-between mb-5">
        <div>
          <p className="text-[10px] uppercase tracking-wider text-white/40 mb-1">
            Vertical benchmarks · privacy-preserving aggregation
          </p>
          <p className="text-white/90 font-medium">
            Halcyon Apparel vs. DTC fashion cohort
          </p>
        </div>
        <span className="text-[10px] text-rose-300/80 font-mono px-2 py-1 bg-rose-500/10 rounded">
          Phase 4b
        </span>
      </div>

      <div className="grid sm:grid-cols-3 gap-3">
        {benchmarkCards.map((b, i) => (
          <motion.div
            key={b.metric}
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.5, delay: i * 0.12 }}
            className="rounded-xl bg-[#0a162e]/60 border border-white/5 p-4 flex flex-col"
          >
            <p className="text-[10px] uppercase tracking-wider text-white/40 mb-2">
              {b.metric}
            </p>
            <p className="text-2xl font-bold text-white">{b.yourValue}</p>
            <p className="text-[10px] text-white/40 mt-0.5">
              cohort median {b.median}
            </p>

            <div className="mt-4">
              <p className="text-[10px] uppercase tracking-wider text-white/40 mb-1.5">
                Percentile
              </p>
              <div className="relative h-1.5 bg-white/10 rounded overflow-hidden mb-2">
                <motion.div
                  initial={{ scaleX: 0 }}
                  whileInView={{ scaleX: b.percentile / 100 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.8, delay: 0.3 + i * 0.12 }}
                  style={{ originX: 0 }}
                  className={`h-full rounded ${
                    b.percentile >= 75 ? "bg-emerald-400" : b.percentile >= 50 ? "bg-teal-400" : b.percentile >= 25 ? "bg-amber-400" : "bg-rose-400"
                  }`}
                />
              </div>
              <span className={`inline-block text-[10px] font-mono px-2 py-0.5 rounded ${pillCls(b.percentile)}`}>
                {b.percentile}th percentile
              </span>
            </div>

            <p className="text-[10px] text-white/40 mt-3 leading-relaxed">{b.cohort}</p>
          </motion.div>
        ))}
      </div>

      <div className="mt-5 px-4 py-3 rounded-lg bg-white/[0.025] border border-white/10 text-[11px] text-white/55 leading-relaxed">
        <span className="font-semibold text-white/85">12+ DTC fashion agencies</span> ·
        differential privacy applied · individual agency ROAS never derivable.
        Warm-start priors derived from cohort for new clients in this vertical.
      </div>
    </div>
  );
}
