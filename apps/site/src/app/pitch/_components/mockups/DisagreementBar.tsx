"use client";

import { motion } from "motion/react";

export function DisagreementBar() {
  return (
    <div className="w-full bg-white/[0.03] border border-white/10 rounded-xl p-5">
      <p className="text-[10px] uppercase tracking-wider text-white/40 mb-3">
        Meta — Prospecting · Halcyon US
      </p>

      <div className="space-y-3">
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-[11px] text-teal-300/90">Mode A · Platform</span>
            <span className="text-xs font-mono text-white/85">$41 CPA</span>
          </div>
          <motion.div
            initial={{ scaleX: 0 }}
            whileInView={{ scaleX: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
            style={{ originX: 0 }}
            className="h-1.5 rounded-full bg-teal-400"
          />
        </div>

        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="text-[11px] text-amber-300/90">Mode B · GA4</span>
            <span className="text-xs font-mono text-white/85">$44 CPA</span>
          </div>
          <motion.div
            initial={{ scaleX: 0 }}
            whileInView={{ scaleX: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.15, ease: [0.22, 1, 0.36, 1] }}
            style={{ originX: 0 }}
            className="h-1.5 rounded-full bg-amber-400"
          />
        </div>
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ delay: 0.6 }}
        className="mt-4 flex items-center justify-between text-[10px] text-white/50"
      >
        <span>Δ 7.3%</span>
        <span className="inline-flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
          Tight cluster · agreement
        </span>
      </motion.div>
    </div>
  );
}
