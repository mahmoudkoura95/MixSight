"use client";

import { motion } from "motion/react";

const options = [
  { rank: 1, label: "Halcyon UK · TikTok → Meta", impact: "+92 conv", confidence: 0.84 },
  { rank: 2, label: "Stratton US · PMax → Remarket", impact: "+$28K rev", confidence: 0.62 },
  { rank: 3, label: "Halcyon · cross-market", impact: "+178 conv", confidence: 0.38 },
];

export function OptionsNotRecommendations() {
  return (
    <div className="w-full bg-white/[0.03] border border-white/10 rounded-xl p-5">
      <p className="text-[10px] uppercase tracking-wider text-white/40 mb-4">
        Three options · evidence-backed
      </p>
      <div className="space-y-2">
        {options.map((o, i) => (
          <motion.div
            key={o.rank}
            initial={{ opacity: 0, x: -8 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: i * 0.1 }}
            className="flex items-center gap-3 px-3 py-2 rounded-lg bg-white/[0.04] border border-white/5"
          >
            <span className="w-5 h-5 rounded-full bg-teal-400/20 text-teal-300 text-[10px] flex items-center justify-center font-bold">
              {o.rank}
            </span>
            <div className="flex-1 min-w-0">
              <p className="text-[11px] text-white/80 truncate">{o.label}</p>
              <div className="flex items-center gap-2 mt-1">
                <div className="flex-1 h-0.5 bg-white/10 rounded">
                  <motion.div
                    initial={{ scaleX: 0 }}
                    whileInView={{ scaleX: o.confidence }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6, delay: 0.4 + i * 0.1 }}
                    style={{ originX: 0 }}
                    className="h-full rounded bg-teal-400"
                  />
                </div>
                <span className="text-[10px] text-white/40 font-mono tabular-nums">
                  {Math.round(o.confidence * 100)}%
                </span>
              </div>
            </div>
            <span className="text-[10px] text-white/60 font-mono whitespace-nowrap">
              {o.impact}
            </span>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
