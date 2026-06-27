"use client";

import { motion } from "motion/react";

// Abstract world dots — three illuminated markets (US, UK, AU) on a stylized grid.
const markets: { id: string; label: string; x: number; y: number; lit: boolean }[] = [
  { id: "us-ny", label: "US-NY", x: 24, y: 38, lit: true },
  { id: "us-la", label: "US-LA", x: 12, y: 44, lit: true },
  { id: "uk", label: "UK", x: 50, y: 30, lit: true },
  { id: "de", label: "DE", x: 56, y: 32, lit: false },
  { id: "ae", label: "AE", x: 64, y: 48, lit: false },
  { id: "au", label: "AU", x: 86, y: 72, lit: true },
];

export function MultiMarketMap() {
  return (
    <div className="w-full bg-white/[0.03] border border-white/10 rounded-xl p-5">
      <p className="text-[10px] uppercase tracking-wider text-white/40 mb-3">
        Markets · per-locale settings · live FX
      </p>
      <div className="relative w-full aspect-[2/1] rounded-lg overflow-hidden bg-white/[0.02]">
        {/* Grid texture */}
        <div
          aria-hidden
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage:
              "linear-gradient(rgba(255,255,255,0.15) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.15) 1px, transparent 1px)",
            backgroundSize: "16px 16px",
          }}
        />
        {markets.map((m, i) => (
          <motion.div
            key={m.id}
            initial={{ opacity: 0, scale: 0 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: i * 0.08 }}
            className="absolute flex flex-col items-center -translate-x-1/2 -translate-y-1/2"
            style={{ left: `${m.x}%`, top: `${m.y}%` }}
          >
            <span
              className={`w-2.5 h-2.5 rounded-full ${
                m.lit ? "bg-teal-400 shadow-[0_0_12px_3px_rgba(45,212,191,0.45)]" : "bg-white/20"
              }`}
            />
            <span
              className={`text-[9px] mt-1 uppercase tracking-wider ${
                m.lit ? "text-teal-200" : "text-white/30"
              }`}
            >
              {m.label}
            </span>
          </motion.div>
        ))}
      </div>
      <div className="mt-3 flex items-center justify-between text-[10px] text-white/40">
        <span>Per-market local TZ pull</span>
        <span>FX daily refresh</span>
      </div>
    </div>
  );
}
