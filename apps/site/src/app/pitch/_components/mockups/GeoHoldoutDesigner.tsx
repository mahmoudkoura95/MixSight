"use client";

import { motion } from "motion/react";

const candidates = [
  { control: "Boston MSA", test: "Philadelphia MSA", similarity: 0.92, lift: "12%+", duration: "6 weeks" },
  { control: "Atlanta MSA", test: "Charlotte MSA", similarity: 0.87, lift: "14%+", duration: "7 weeks" },
  { control: "Seattle MSA", test: "Portland MSA", similarity: 0.81, lift: "16%+", duration: "8 weeks" },
];

export function GeoHoldoutDesigner() {
  return (
    <div className="w-full bg-white/[0.025] border border-white/10 rounded-2xl p-6 shadow-2xl">
      <div className="flex items-center justify-between mb-4">
        <div>
          <p className="text-[10px] uppercase tracking-wider text-white/40 mb-1">
            Geo holdout designer · Halcyon US Meta Prospecting
          </p>
          <p className="text-white/90 font-medium">Test budget: $40K · target power: 80%</p>
        </div>
        <span className="text-[10px] text-indigo-300/80 font-mono px-2 py-1 bg-indigo-500/10 rounded">
          Phase 3d
        </span>
      </div>

      <div className="space-y-2.5">
        {candidates.map((c, i) => (
          <motion.div
            key={c.control}
            initial={{ opacity: 0, y: 8 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-50px" }}
            transition={{ duration: 0.5, delay: i * 0.12 }}
            className={`rounded-xl border p-4 ${
              i === 0
                ? "border-teal-400/40 bg-teal-500/5"
                : "border-white/10 bg-white/[0.02]"
            }`}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-3">
                {i === 0 && (
                  <span className="text-[10px] uppercase tracking-wider text-teal-300 font-semibold px-1.5 py-0.5 rounded bg-teal-500/20">
                    Recommended
                  </span>
                )}
                <p className="text-sm text-white/90">
                  <span className="font-medium">{c.control}</span>
                  <span className="text-white/40 mx-2">vs.</span>
                  <span className="font-medium">{c.test}</span>
                </p>
              </div>
              <span className="text-[10px] font-mono text-white/55">{c.duration}</span>
            </div>

            <div className="flex items-center gap-4">
              <div className="flex-1">
                <div className="flex items-center justify-between text-[10px] uppercase tracking-wider mb-1">
                  <span className="text-white/40">Market similarity</span>
                  <span className="text-white/65 font-mono normal-case">
                    {(c.similarity * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="h-1.5 bg-white/10 rounded overflow-hidden">
                  <motion.div
                    initial={{ scaleX: 0 }}
                    whileInView={{ scaleX: c.similarity }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: 0.3 + i * 0.12 }}
                    style={{ originX: 0 }}
                    className={`h-full rounded ${
                      c.similarity > 0.9 ? "bg-emerald-400" : c.similarity > 0.85 ? "bg-teal-400" : "bg-amber-400"
                    }`}
                  />
                </div>
              </div>

              <div className="text-right">
                <p className="text-[10px] uppercase tracking-wider text-white/40">
                  Detectable lift
                </p>
                <p className="text-sm font-semibold text-white">{c.lift}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="mt-5 px-4 py-3 rounded-lg bg-white/[0.025] border border-white/10 text-[11px] text-white/55 leading-relaxed">
        <span className="font-semibold text-white/85">Once the test runs</span> · results
        calibrate the MMM at next refit. Lift estimate enters the evidence column as
        the 4th indicator with a 95% confidence interval.
      </div>
    </div>
  );
}
