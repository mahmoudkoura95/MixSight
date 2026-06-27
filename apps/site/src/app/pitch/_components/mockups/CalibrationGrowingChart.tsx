"use client";

import { motion } from "motion/react";

// Line growing rightward with credible-interval ribbon narrowing.
export function CalibrationGrowingChart() {
  return (
    <div className="w-full bg-white/[0.03] border border-white/10 rounded-xl p-5">
      <p className="text-[10px] uppercase tracking-wider text-white/40 mb-3">
        Predicted vs. actual · 24-month track record
      </p>
      <svg viewBox="0 0 240 80" className="w-full h-auto" preserveAspectRatio="none">
        <defs>
          <linearGradient id="cal-fade" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="rgba(45,212,191,0.0)" />
            <stop offset="20%" stopColor="rgba(45,212,191,0.4)" />
            <stop offset="100%" stopColor="rgba(45,212,191,1)" />
          </linearGradient>
        </defs>

        {/* CI ribbon — narrows over time */}
        <motion.path
          d="M 0 50 Q 60 50 120 42 T 240 36 L 240 28 Q 180 30 120 32 T 0 38 Z"
          fill="rgba(45,212,191,0.10)"
          initial={{ pathLength: 0, opacity: 0 }}
          whileInView={{ pathLength: 1, opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 1.4 }}
        />

        {/* Centerline */}
        <motion.path
          d="M 0 50 Q 60 50 120 42 T 240 36"
          stroke="url(#cal-fade)"
          strokeWidth="1.5"
          fill="none"
          initial={{ pathLength: 0 }}
          whileInView={{ pathLength: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 1.4 }}
        />

        {/* Markers */}
        {[20, 80, 140, 200].map((cx, i) => (
          <motion.circle
            key={cx}
            cx={cx}
            cy={50 - i * 3.5}
            r="2"
            fill="rgb(94,234,212)"
            initial={{ opacity: 0, scale: 0 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 + i * 0.12 }}
          />
        ))}

        {/* x-axis ticks */}
        <line x1="0" y1="76" x2="240" y2="76" stroke="rgba(255,255,255,0.1)" />
      </svg>
      <div className="flex items-center justify-between text-[10px] text-white/40 mt-2">
        <span>Phase 1 launch</span>
        <span>Phase 4 launch</span>
      </div>
    </div>
  );
}
