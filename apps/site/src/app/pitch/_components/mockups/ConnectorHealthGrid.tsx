"use client";

import { motion } from "motion/react";
import { connectorHealth } from "../../_lib/mockData";

const statusStyle: Record<string, { dot: string; label: string; text: string }> = {
  healthy: { dot: "bg-emerald-400", label: "Healthy", text: "text-emerald-300" },
  reauth_due: { dot: "bg-amber-400", label: "Reauth in 6d", text: "text-amber-300" },
  failing: { dot: "bg-rose-400", label: "Failing", text: "text-rose-300" },
};

function parseBackfill(s: string): number {
  // "24 / 24 months" → 1.0
  const m = s.match(/(\d+)\s*\/\s*(\d+)/);
  if (!m) return 0;
  return Math.min(1, Number(m[1]) / Number(m[2]));
}

export function ConnectorHealthGrid() {
  return (
    <div className="w-full bg-white/[0.025] border border-white/10 rounded-2xl p-6 shadow-2xl">
      <div className="flex items-center justify-between mb-5">
        <div>
          <p className="text-[10px] uppercase tracking-wider text-white/40 mb-1">
            Connector health · Halcyon Apparel
          </p>
          <p className="text-white/90 font-medium">
            US + UK · 4 platforms · Org OAuth shared across clients
          </p>
        </div>
        <span className="text-[10px] text-white/40 font-mono hidden sm:block">
          Daily 7d · Weekly 90d · Monthly 13mo
        </span>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {connectorHealth.map((c, i) => {
          const s = statusStyle[c.status] ?? statusStyle.healthy;
          const fill = parseBackfill(c.backfill);
          return (
            <motion.div
              key={`${c.platform}-${c.market}`}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.4, delay: i * 0.06 }}
              className="rounded-xl bg-white/[0.025] border border-white/10 p-4"
            >
              <div className="flex items-center justify-between mb-3">
                <div>
                  <p className="text-white/90 font-medium text-sm">{c.platform}</p>
                  <p className="text-[10px] text-white/40 uppercase tracking-wider">
                    Market · {c.market}
                  </p>
                </div>
                <span className={`inline-flex items-center gap-1.5 text-[10px] ${s.text}`}>
                  <span className={`w-1.5 h-1.5 rounded-full ${s.dot} animate-pulse`} />
                  {s.label}
                </span>
              </div>

              <div className="space-y-1.5 text-[11px]">
                <div className="flex items-center justify-between">
                  <span className="text-white/40">Last pull</span>
                  <span className="font-mono text-white/75">{c.lastPull}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-white/40">Next pull</span>
                  <span className="font-mono text-white/75">{c.nextPull}</span>
                </div>
              </div>

              <div className="mt-3">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-[10px] text-white/40 uppercase tracking-wider">
                    Backfill
                  </span>
                  <span className="text-[10px] text-white/55 font-mono">{c.backfill}</span>
                </div>
                <div className="h-1 bg-white/10 rounded overflow-hidden">
                  <motion.div
                    initial={{ scaleX: 0 }}
                    whileInView={{ scaleX: 1 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.8, delay: 0.3 + i * 0.06 }}
                    style={{ originX: 0, width: `${fill * 100}%` }}
                    className="h-full bg-teal-400 rounded"
                  />
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
