"use client";

import { motion } from "motion/react";

export function DefenseKitMini() {
  return (
    <div className="w-full bg-white/[0.03] border border-white/10 rounded-xl p-5 flex items-center justify-center min-h-[180px]">
      <div className="relative w-32 h-44">
        {[2, 1, 0].map((depth) => (
          <motion.div
            key={depth}
            initial={{ opacity: 0, y: 20, rotate: depth === 0 ? 0 : (depth === 1 ? -3 : 3) }}
            whileInView={{ opacity: 1, y: 0, rotate: depth === 0 ? 0 : (depth === 1 ? -4 : 4) }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1 * (2 - depth) }}
            className="absolute inset-0 bg-white rounded-md p-3 shadow-2xl"
            style={{
              zIndex: 10 - depth,
              transform: `translateY(${depth * 6}px) translateX(${depth * 4}px)`,
            }}
          >
            {depth === 0 && (
              <div className="flex flex-col h-full">
                <div className="h-1.5 w-12 bg-teal-500 rounded-full mb-2" />
                <div className="space-y-1 mb-2">
                  <div className="h-1 w-full bg-slate-200 rounded" />
                  <div className="h-1 w-5/6 bg-slate-200 rounded" />
                  <div className="h-1 w-4/6 bg-slate-200 rounded" />
                </div>
                <div className="space-y-0.5 mt-1">
                  <div className="h-1 w-full bg-emerald-200 rounded" />
                  <div className="h-1 w-full bg-amber-200 rounded" />
                  <div className="h-1 w-full bg-rose-200 rounded" />
                  <div className="h-1 w-full bg-slate-100 rounded" />
                </div>
                <div className="mt-auto flex items-center gap-1">
                  <div className="h-1 w-3 bg-slate-300 rounded-full" />
                  <div className="h-1 w-6 bg-slate-300 rounded-full" />
                </div>
              </div>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
}
