"use client";

import { motion } from "motion/react";
import { Check } from "lucide-react";
import { pricingCopy } from "../../_lib/content";

export function Pricing() {
  return (
    <section
      id="pricing"
      className="relative py-28 md:py-36 px-4 sm:px-6 lg:px-8 border-t border-white/5 scroll-mt-16"
    >
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.5 }}
          className="text-center mb-16"
        >
          <p className="text-[11px] uppercase tracking-[0.2em] text-teal-300/70 mb-3">
            Pricing · §4
          </p>
          <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-5">
            {pricingCopy.headline}
          </h2>
          <p className="text-lg text-white/60 max-w-2xl mx-auto leading-relaxed">
            {pricingCopy.intro}
          </p>
        </motion.div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {pricingCopy.tiers.map((t, i) => {
            const highlight = "highlight" in t && t.highlight;
            return (
              <motion.div
                key={t.name}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ duration: 0.5, delay: i * 0.08 }}
                className={`relative rounded-2xl border p-6 flex flex-col ${
                  highlight
                    ? "border-teal-400/40 bg-gradient-to-b from-teal-500/[0.08] to-transparent"
                    : "border-white/10 bg-white/[0.025]"
                }`}
              >
                {highlight && (
                  <span className="absolute -top-2.5 left-1/2 -translate-x-1/2 px-2.5 py-0.5 rounded-full bg-teal-400 text-[#0f1e3d] text-[10px] uppercase tracking-wider font-bold">
                    Best fit · design partner
                  </span>
                )}

                <p className="text-[11px] uppercase tracking-[0.18em] text-white/40 mb-2">
                  {t.name}
                </p>
                <div className="flex items-baseline gap-1 mb-1">
                  <span className="text-3xl font-bold text-white">{t.price}</span>
                  <span className="text-sm text-white/40">{t.cadence}</span>
                </div>
                <p className="text-[11px] text-white/45 leading-relaxed mb-5 min-h-[42px]">
                  {t.blurb}
                </p>

                <ul className="space-y-2 text-[11px] mt-auto">
                  <Row label="Seats" value={t.seats} />
                  <Row label="Workspaces" value={t.workspaces} />
                  <Row label="LLM quota" value={t.llm} />
                  <Row
                    label="White-label"
                    value={typeof t.whitelabel === "string" ? t.whitelabel : "Not included"}
                    muted={!t.whitelabel}
                  />
                </ul>
              </motion.div>
            );
          })}
        </div>

        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mt-10 rounded-2xl bg-white/[0.025] border border-white/10 px-6 py-5 flex items-start gap-3"
        >
          <Check className="w-4 h-4 text-teal-300 mt-1 flex-shrink-0" aria-hidden />
          <p className="text-sm text-white/65 leading-relaxed">
            <span className="font-semibold text-white/90">BYOK · Growth and above.</span>{" "}
            {pricingCopy.byokNote}
          </p>
        </motion.div>
      </div>
    </section>
  );
}

function Row({ label, value, muted }: { label: string; value: string; muted?: boolean }) {
  return (
    <li className="flex items-start justify-between gap-2">
      <span className="text-white/40">{label}</span>
      <span className={`text-right ${muted ? "text-white/30" : "text-white/85"}`}>
        {value}
      </span>
    </li>
  );
}
