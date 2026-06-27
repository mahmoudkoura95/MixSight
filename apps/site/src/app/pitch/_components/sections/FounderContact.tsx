"use client";

import { motion } from "motion/react";
import { Mail, Calendar, ArrowUpRight } from "lucide-react";
import { founderCopy } from "../../_lib/content";

export function FounderContact() {
  return (
    <section
      id="contact"
      className="relative py-28 md:py-36 px-4 sm:px-6 lg:px-8 border-t border-white/5 scroll-mt-16"
    >
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          className="rounded-3xl border border-white/10 bg-gradient-to-br from-white/[0.04] to-white/[0.01] p-8 md:p-12"
        >
          <p className="text-[11px] uppercase tracking-[0.2em] text-teal-300/80 mb-3">
            {founderCopy.eyebrow}
          </p>
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-6 leading-tight">
            {founderCopy.headline}
          </h2>

          <div className="space-y-4 mb-8">
            {founderCopy.body.map((p, i) => (
              <motion.p
                key={i}
                initial={{ opacity: 0, y: 8 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: 0.1 + i * 0.1 }}
                className="text-base md:text-lg text-white/70 leading-relaxed"
              >
                {p}
              </motion.p>
            ))}
          </div>

          <div className="flex flex-col sm:flex-row gap-3 pt-4 border-t border-white/10">
            <a
              href={founderCopy.schedulerUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="group inline-flex items-center justify-center gap-2 px-5 py-3 rounded-lg bg-teal-400 hover:bg-teal-300 text-[#0f1e3d] font-semibold text-sm transition-colors"
            >
              <Calendar className="w-4 h-4" aria-hidden />
              {founderCopy.schedulerLabel}
              <ArrowUpRight className="w-3.5 h-3.5 -mr-1 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" aria-hidden />
            </a>
            <a
              href={`mailto:${founderCopy.email}?subject=MixSight%20%C2%B7%20Design%20partner%20interest`}
              className="inline-flex items-center justify-center gap-2 px-5 py-3 rounded-lg bg-white/5 hover:bg-white/10 border border-white/15 text-white font-medium text-sm transition-colors"
            >
              <Mail className="w-4 h-4" aria-hidden />
              {founderCopy.emailLabel}
              <span className="text-white/50 font-mono text-xs">· {founderCopy.email}</span>
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
