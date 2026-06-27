"use client";

import { motion } from "motion/react";
import Image from "next/image";
import { Lock } from "lucide-react";
import { footerCopy } from "../../_lib/content";

export function PitchFooter() {
  return (
    <footer className="relative border-t border-white/10 bg-[#0a162e]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        {/* Confidential stripe */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="flex items-center gap-2.5 px-4 py-3 rounded-lg bg-amber-500/10 border border-amber-500/25 text-amber-200 text-xs mb-8"
        >
          <Lock className="w-3.5 h-3.5 flex-shrink-0" aria-hidden />
          <span className="leading-relaxed">{footerCopy.privacyStripe}</span>
        </motion.div>

        <div className="flex flex-col md:flex-row justify-between gap-8 md:gap-12">
          <div>
            <div className="bg-white rounded-md px-2.5 py-1.5 inline-block mb-3">
              <Image src="/logo.png" alt="MixSight" width={100} height={26} />
            </div>
            <p className="text-xs text-white/40 leading-relaxed max-w-sm">
              {footerCopy.citation}
            </p>
          </div>

          <div>
            <p className="text-[10px] uppercase tracking-[0.2em] text-white/40 mb-3">
              Source · SCOPE.md
            </p>
            <ul className="grid grid-cols-2 gap-x-6 gap-y-1.5 text-xs">
              {footerCopy.citationLinks.map((c) => (
                <li key={c.label} className="flex items-center justify-between">
                  <span className="text-white/55">{c.label}</span>
                  <span className="text-white/40 font-mono">{c.section}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="mt-10 pt-6 border-t border-white/5 flex flex-col md:flex-row justify-between gap-2 text-[10px] uppercase tracking-wider text-white/35">
          <span>Last updated · {footerCopy.lastUpdated}</span>
          <span>mixsight.ai · noindex · do not redistribute</span>
        </div>
      </div>
    </footer>
  );
}
