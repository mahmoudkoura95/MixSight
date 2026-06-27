"use client";

import { motion } from "motion/react";

const days = [
  { label: "M", solid: true, height: 38 },
  { label: "T", solid: true, height: 52 },
  { label: "W", solid: true, height: 46 },
  { label: "T", solid: true, height: 60 },
  { label: "F", solid: false, height: 44 },
  { label: "S", solid: false, height: 36 },
  { label: "S", solid: false, height: 28 },
];

export function FreshnessUXSplit() {
  return (
    <div className="w-full bg-white/[0.03] border border-white/10 rounded-xl p-5">
      <p className="text-[10px] uppercase tracking-wider text-white/40 mb-4">
        Current week · trailing 3 days muted
      </p>

      <div className="flex items-end gap-1.5 h-20">
        {days.map((d, i) => (
          <div key={i} className="flex-1 flex flex-col items-center gap-1.5">
            <motion.div
              initial={{ scaleY: 0 }}
              whileInView={{ scaleY: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.06 }}
              style={{ originY: 1, height: `${d.height}px` }}
              className={`w-full rounded-t ${
                d.solid
                  ? "bg-teal-400"
                  : "bg-teal-400/30 border-t border-dashed border-teal-300/60"
              }`}
            />
            <span
              className={`text-[10px] font-medium ${
                d.solid ? "text-white/70" : "text-white/30 italic"
              }`}
            >
              {d.label}
            </span>
          </div>
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ delay: 0.6 }}
        className="mt-4 flex items-center justify-between text-[10px]"
      >
        <span className="inline-flex items-center gap-1.5 text-teal-300/80">
          <span className="w-1.5 h-1.5 rounded-full bg-teal-400" />
          Settled
        </span>
        <span className="inline-flex items-center gap-1.5 text-white/40">
          <span className="w-1.5 h-1.5 rounded-full bg-teal-400/30 border border-dashed border-teal-300/60" />
          Still settling
        </span>
      </motion.div>
    </div>
  );
}
