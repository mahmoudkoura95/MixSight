"use client";

import { motion } from "motion/react";

const changes = [
  { label: "v1 ingested", date: "Apr 03" },
  { label: "Meta +$8K (client ask)", date: "Apr 14" },
  { label: "UK TikTok launched", date: "Apr 24" },
  { label: "PMax cap reduced", date: "May 06" },
];

export function PlanChangeTimeline() {
  return (
    <div className="w-full bg-white/[0.03] border border-white/10 rounded-xl p-5">
      <p className="text-[10px] uppercase tracking-wider text-white/40 mb-5">
        Plan revisions · audit trail
      </p>
      <div className="relative pt-2">
        {/* Line */}
        <motion.div
          initial={{ scaleX: 0 }}
          whileInView={{ scaleX: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 1, ease: "easeOut" }}
          style={{ originX: 0 }}
          className="absolute top-3 left-0 right-0 h-px bg-gradient-to-r from-teal-400/80 via-teal-400/40 to-teal-400/10"
        />
        {/* Notches */}
        <div className="flex items-start justify-between">
          {changes.map((c, i) => (
            <motion.div
              key={c.date}
              initial={{ opacity: 0, y: 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: 0.2 + i * 0.15 }}
              className="flex flex-col items-center relative"
              style={{ flexBasis: "25%" }}
            >
              <span className="w-2.5 h-2.5 rounded-full bg-teal-400 shadow-[0_0_8px_2px_rgba(45,212,191,0.4)]" />
              <span className="mt-3 text-[10px] text-white/70 text-center px-1 leading-tight">
                {c.label}
              </span>
              <span className="text-[9px] text-white/35 mt-0.5">{c.date}</span>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
