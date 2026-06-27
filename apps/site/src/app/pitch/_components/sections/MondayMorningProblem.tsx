"use client";

import { motion, useReducedMotion } from "motion/react";
import { Clock, Check, X, FileSpreadsheet, FileCheck2 } from "lucide-react";
import { problemCopy } from "../../_lib/content";

export function MondayMorningProblem() {
  const reduced = useReducedMotion();

  return (
    <section
      id="problem"
      className="relative py-28 md:py-36 px-4 sm:px-6 lg:px-8 border-t border-white/5 scroll-mt-16"
    >
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.5 }}
          className="text-center mb-20"
        >
          <p className="text-xs uppercase tracking-[0.2em] text-teal-300/70 mb-3">
            The Monday morning workflow
          </p>
          <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-5">
            {problemCopy.headline}
          </h2>
          <p className="text-lg text-white/60 max-w-2xl mx-auto leading-relaxed">
            {problemCopy.intro}
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-6 md:gap-8 items-start">
          {/* TODAY column */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.6 }}
            className="relative bg-gradient-to-br from-rose-500/10 to-rose-900/5 border border-rose-500/20 rounded-2xl p-7"
          >
            <div className="flex items-center justify-between mb-7">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-rose-500/20 flex items-center justify-center">
                  <FileSpreadsheet className="w-5 h-5 text-rose-300" aria-hidden />
                </div>
                <div>
                  <p className="text-[11px] uppercase tracking-wider text-rose-300/70">
                    {problemCopy.before.label}
                  </p>
                  <p className="font-semibold text-white">In Sheets</p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-rose-200/80">
                <Clock className="w-4 h-4" aria-hidden />
                <span className="text-sm font-mono tabular-nums">
                  {problemCopy.before.duration}
                </span>
              </div>
            </div>

            <ul className="space-y-2.5">
              {problemCopy.before.steps.map((step, i) => (
                <motion.li
                  key={step}
                  initial={{ opacity: 0, x: -8 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true, margin: "-50px" }}
                  transition={{ duration: 0.3, delay: reduced ? 0 : 0.05 * i }}
                  className="flex items-start gap-2.5 text-sm text-white/75"
                >
                  <X
                    className="w-3.5 h-3.5 mt-1 text-rose-400/70 flex-shrink-0"
                    aria-hidden
                  />
                  <span className="leading-relaxed">{step}</span>
                </motion.li>
              ))}
            </ul>
          </motion.div>

          {/* WITH MIXSIGHT column */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ duration: 0.6, delay: reduced ? 0 : 0.15 }}
            className="relative bg-gradient-to-br from-teal-500/15 to-emerald-900/5 border border-teal-400/30 rounded-2xl p-7"
          >
            <div className="absolute -top-3 right-6 px-2.5 py-1 rounded-full bg-teal-400 text-[#0f1e3d] text-[10px] uppercase tracking-wider font-bold">
              The wedge
            </div>

            <div className="flex items-center justify-between mb-7">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-teal-400/20 flex items-center justify-center">
                  <FileCheck2 className="w-5 h-5 text-teal-300" aria-hidden />
                </div>
                <div>
                  <p className="text-[11px] uppercase tracking-wider text-teal-300/80">
                    {problemCopy.after.label}
                  </p>
                  <p className="font-semibold text-white">Monday workflow</p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-teal-200">
                <Clock className="w-4 h-4" aria-hidden />
                <span className="text-sm font-mono tabular-nums">
                  {problemCopy.after.duration}
                </span>
              </div>
            </div>

            <ul className="space-y-2.5">
              {problemCopy.after.steps.map((step, i) => (
                <motion.li
                  key={step}
                  initial={{ opacity: 0, x: 8 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true, margin: "-50px" }}
                  transition={{ duration: 0.3, delay: reduced ? 0 : 0.05 * i + 0.2 }}
                  className="flex items-start gap-2.5 text-sm text-white/85"
                >
                  <Check
                    className="w-3.5 h-3.5 mt-1 text-teal-300 flex-shrink-0"
                    aria-hidden
                  />
                  <span className="leading-relaxed">{step}</span>
                </motion.li>
              ))}
            </ul>
          </motion.div>
        </div>

        {/* Bottom callout */}
        <motion.p
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true, margin: "-50px" }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="text-center text-xs uppercase tracking-[0.18em] text-white/40 mt-12"
        >
          Same AM · Same client · Same data · 8× faster · Defensible at the end
        </motion.p>
      </div>
    </section>
  );
}
