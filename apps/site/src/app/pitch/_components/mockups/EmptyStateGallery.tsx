"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "motion/react";
import { Sparkles, Clock3, CalendarOff, CalendarCheck, AlertCircle } from "lucide-react";
import { emptyStates } from "../../_lib/mockData";

const iconFor: Record<string, React.ReactNode> = {
  backfill: <Sparkles className="w-5 h-5" aria-hidden />,
  "partial-week": <Clock3 className="w-5 h-5" aria-hidden />,
  "pre-flight": <CalendarOff className="w-5 h-5" aria-hidden />,
  "post-flight": <CalendarCheck className="w-5 h-5" aria-hidden />,
  "insufficient-data": <AlertCircle className="w-5 h-5" aria-hidden />,
};

export function EmptyStateGallery() {
  const [index, setIndex] = useState(0);
  const reduced = useReducedMotion();

  useEffect(() => {
    const id = setInterval(() => {
      setIndex((i) => (i + 1) % emptyStates.length);
    }, reduced ? 5500 : 4200);
    return () => clearInterval(id);
  }, [reduced]);

  const current = emptyStates[index];

  return (
    <div className="w-full bg-white/[0.025] border border-white/10 rounded-2xl p-6 shadow-2xl">
      <div className="flex items-center justify-between mb-4">
        <p className="text-[10px] uppercase tracking-wider text-white/40">
          Empty states · §7.18
        </p>
        <div className="flex gap-1">
          {emptyStates.map((s, i) => (
            <button
              key={s.id}
              onClick={() => setIndex(i)}
              aria-label={`Show ${s.title}`}
              className={`h-1 transition-all rounded-full ${
                i === index ? "w-8 bg-teal-400" : "w-3 bg-white/15 hover:bg-white/30"
              }`}
            />
          ))}
        </div>
      </div>

      <div className="relative h-44">
        <AnimatePresence mode="wait">
          <motion.div
            key={current.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
            className="absolute inset-0 rounded-xl bg-gradient-to-br from-white/[0.04] to-white/[0.01] border border-white/10 p-5 flex flex-col"
          >
            <div className="flex items-center gap-3 mb-3">
              <span className="w-10 h-10 rounded-lg bg-teal-400/15 text-teal-300 flex items-center justify-center">
                {iconFor[current.id]}
              </span>
              <div>
                <p className="text-white/90 font-semibold leading-tight">{current.title}</p>
                <p className="text-[10px] text-white/40 mt-0.5">{current.cite}</p>
              </div>
            </div>
            <p className="text-sm text-white/65 leading-relaxed">{current.body}</p>

            {/* Visual placeholder strip */}
            <div className="mt-auto pt-4">
              <div className="h-px bg-white/10 mb-3" />
              <div className="space-y-1.5">
                <div className="h-1.5 w-3/4 bg-white/10 rounded" />
                <div className="h-1.5 w-1/2 bg-white/10 rounded" />
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      <p className="text-[10px] text-white/40 mt-3 text-center">
        Auto-cycling · click a dot to jump
      </p>
    </div>
  );
}
