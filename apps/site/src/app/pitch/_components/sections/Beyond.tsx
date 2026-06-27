"use client";

import { motion } from "motion/react";
import { Sparkles, ArrowRight } from "lucide-react";
import { beyondCopy } from "../../_lib/content";

export function Beyond() {
  return (
    <section
      id="beyond"
      className="relative py-28 md:py-36 px-4 sm:px-6 lg:px-8 border-t border-white/5 scroll-mt-16 overflow-hidden"
    >
      {/* Background flourish */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[80vw] h-[80vw] max-w-[1100px] max-h-[1100px]">
          <div className="absolute inset-0 rounded-full bg-gradient-to-tr from-teal-500/[0.06] to-purple-500/[0.05] blur-3xl" />
        </div>
      </div>

      <div className="relative max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16 max-w-3xl mx-auto"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/5 border border-white/10 rounded-full mb-5">
            <Sparkles className="w-3.5 h-3.5 text-teal-300" aria-hidden />
            <span className="text-[11px] tracking-[0.18em] uppercase text-teal-300/80">
              {beyondCopy.label} · {beyondCopy.months}
            </span>
          </div>
          <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-5">
            {beyondCopy.northStar}
          </h2>
          <p className="text-base md:text-lg text-white/55 leading-relaxed">
            The wedge holds. The depth compounds. By year 3, MixSight is the
            measurement substrate for mid-tier performance agencies — and the
            calibration record makes that defensible.
          </p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {beyondCopy.items.map((it, i) => (
            <motion.div
              key={it.title}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-50px" }}
              transition={{ duration: 0.5, delay: i * 0.08 }}
              className="group relative rounded-2xl bg-white/[0.025] border border-white/10 p-6 hover:border-teal-400/30 transition-colors"
            >
              <div className="flex items-start justify-between mb-4">
                <span className="inline-flex items-center justify-center w-9 h-9 rounded-lg bg-teal-400/15 text-teal-300 font-mono text-xs font-bold">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <ArrowRight className="w-4 h-4 text-white/20 group-hover:text-teal-300 group-hover:translate-x-1 transition-all" aria-hidden />
              </div>
              <h3 className="text-base font-semibold tracking-tight mb-2.5 text-white/95">
                {it.title}
              </h3>
              <p className="text-sm text-white/55 leading-relaxed">{it.body}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
