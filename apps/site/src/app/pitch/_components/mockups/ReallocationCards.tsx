"use client";

import { motion } from "motion/react";
import { ArrowRight } from "lucide-react";
import { reallocationSuggestions } from "../../_lib/mockData";

const confidenceColor: Record<string, string> = {
  high: "bg-teal-400",
  medium: "bg-amber-400",
  low: "bg-rose-400",
};

const confidenceWidth: Record<string, string> = {
  high: "82%",
  medium: "58%",
  low: "32%",
};

export function ReallocationCards() {
  return (
    <div className="w-full grid md:grid-cols-3 gap-4">
      {reallocationSuggestions.map((s, i) => (
        <motion.article
          key={s.rank}
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-50px" }}
          transition={{ duration: 0.5, delay: i * 0.12, ease: [0.22, 1, 0.36, 1] }}
          className="relative bg-white/[0.03] border border-white/10 rounded-2xl p-5 flex flex-col"
        >
          <div className="flex items-center justify-between mb-4">
            <span
              className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold ${
                s.rank === 1
                  ? "bg-teal-400 text-[#0f1e3d]"
                  : "bg-white/10 text-white/80"
              }`}
            >
              {s.rank}
            </span>
            <span className="text-[10px] uppercase tracking-wider text-white/40 font-mono">
              {s.scope}
            </span>
          </div>

          <div className="flex items-center gap-2 text-xs mb-4">
            <div className="flex-1 min-w-0 rounded-md bg-rose-500/15 border border-rose-500/25 px-2.5 py-1.5">
              <p className="text-[9px] uppercase tracking-wider text-rose-300/80">Donor</p>
              <p className="text-white/85 truncate text-[11px]">{s.donor.channel}</p>
              <p className="text-[9px] text-rose-200/60">{s.donor.client} · {s.donor.market}</p>
            </div>
            <ArrowRight className="w-4 h-4 text-white/40 flex-shrink-0" aria-hidden />
            <div className="flex-1 min-w-0 rounded-md bg-emerald-500/15 border border-emerald-500/25 px-2.5 py-1.5">
              <p className="text-[9px] uppercase tracking-wider text-emerald-300/80">Receiver</p>
              <p className="text-white/85 truncate text-[11px]">{s.receiver.channel}</p>
              <p className="text-[9px] text-emerald-200/60">{s.receiver.client} · {s.receiver.market}</p>
            </div>
          </div>

          <div className="rounded-md bg-white/[0.02] border border-white/5 p-3 mb-4">
            <p className="text-[10px] uppercase tracking-wider text-white/40">Move</p>
            <p className="text-xl font-bold text-white mt-0.5">${s.amount.toLocaleString()}</p>
            <p className="text-[11px] text-white/70 mt-1.5">
              <span className="font-medium text-teal-300">{s.projectedImpact}</span>{" "}
              <span className="text-white/40 font-mono">{s.projectedRange}</span>
            </p>
          </div>

          <div className="mb-4">
            <div className="flex items-center justify-between mb-1.5">
              <p className="text-[10px] uppercase tracking-wider text-white/40">Confidence</p>
              <p className="text-[10px] uppercase font-semibold text-white/70">
                {s.confidence}
              </p>
            </div>
            <div className="h-1 bg-white/10 rounded overflow-hidden">
              <motion.div
                initial={{ scaleX: 0 }}
                whileInView={{ scaleX: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.7, delay: 0.3 + i * 0.12 }}
                style={{ originX: 0, width: confidenceWidth[s.confidence] }}
                className={`h-full rounded ${confidenceColor[s.confidence]}`}
              />
            </div>
          </div>

          <p className="text-[11px] text-white/55 leading-relaxed">{s.rationale}</p>
        </motion.article>
      ))}
    </div>
  );
}
