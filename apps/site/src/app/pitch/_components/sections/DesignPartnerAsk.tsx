"use client";

import { motion } from "motion/react";
import { Gift, Handshake, Check } from "lucide-react";
import { designPartnerCopy } from "../../_lib/content";

export function DesignPartnerAsk() {
  return (
    <section
      id="partner"
      className="relative py-28 md:py-36 px-4 sm:px-6 lg:px-8 border-t border-white/5 scroll-mt-16 overflow-hidden"
    >
      {/* Decorative ambient */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[40rem] h-[40rem] rounded-full bg-teal-500/[0.08] blur-3xl" />
      </div>

      <div className="relative max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <p className="text-[11px] uppercase tracking-[0.2em] text-teal-300/80 mb-3">
            {designPartnerCopy.eyebrow}
          </p>
          <h2 className="text-4xl md:text-6xl font-bold tracking-tight mb-5 leading-tight">
            {designPartnerCopy.headline}
          </h2>
          <p className="text-lg text-white/65 max-w-2xl mx-auto leading-relaxed">
            {designPartnerCopy.subhead}
          </p>
        </motion.div>

        {/* Two-column give/take */}
        <div className="grid md:grid-cols-2 gap-5 mb-12">
          <Column
            icon={<Gift className="w-5 h-5" aria-hidden />}
            eyebrow="What you get"
            items={designPartnerCopy.whatYouGet}
            tone="teal"
          />
          <Column
            icon={<Handshake className="w-5 h-5" aria-hidden />}
            eyebrow="What we ask"
            items={designPartnerCopy.whatWeAsk}
            tone="white"
          />
        </div>

        {/* Timeline */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-50px" }}
          transition={{ duration: 0.5 }}
          className="rounded-2xl border border-white/10 bg-white/[0.025] p-7 mb-10"
        >
          <p className="text-[11px] uppercase tracking-[0.2em] text-teal-300/80 mb-5 text-center">
            Phase 1 partnership timeline
          </p>
          <div className="relative grid grid-cols-4 gap-2">
            {/* Connecting line */}
            <motion.div
              initial={{ scaleX: 0 }}
              whileInView={{ scaleX: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 1.4, ease: "easeOut" }}
              style={{ originX: 0 }}
              className="absolute top-3 left-[12.5%] right-[12.5%] h-px bg-gradient-to-r from-teal-400/60 via-teal-400/30 to-teal-400/10"
            />
            {designPartnerCopy.timeline.map((step, i) => (
              <motion.div
                key={step.week}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: 0.4 + i * 0.15 }}
                className="flex flex-col items-center"
              >
                <span className="w-6 h-6 rounded-full bg-teal-400 text-[#0f1e3d] text-[10px] font-bold flex items-center justify-center mb-3">
                  {i + 1}
                </span>
                <p className="text-[10px] uppercase tracking-wider text-teal-300/80 mb-1 font-mono">
                  {step.week}
                </p>
                <p className="text-[11px] text-white/70 text-center leading-tight">
                  {step.label}
                </p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Fit checklist */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="rounded-2xl border border-white/10 bg-white/[0.015] p-7"
        >
          <p className="text-[11px] uppercase tracking-[0.2em] text-white/40 mb-4">
            Fit check · ideal partner profile
          </p>
          <ul className="grid sm:grid-cols-2 gap-2.5">
            {designPartnerCopy.fitChecklist.map((item, i) => (
              <motion.li
                key={item}
                initial={{ opacity: 0, x: -4 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.3, delay: i * 0.05 }}
                className="flex items-start gap-2 text-sm text-white/70"
              >
                <Check className="w-4 h-4 text-teal-300 mt-0.5 flex-shrink-0" aria-hidden />
                <span>{item}</span>
              </motion.li>
            ))}
          </ul>
        </motion.div>
      </div>
    </section>
  );
}

function Column({
  icon,
  eyebrow,
  items,
  tone,
}: {
  icon: React.ReactNode;
  eyebrow: string;
  items: { title: string; body: string }[];
  tone: "teal" | "white";
}) {
  const accent = tone === "teal" ? "from-teal-500/15 to-teal-900/5 border-teal-400/30" : "from-white/[0.04] to-white/[0.01] border-white/10";
  const iconBg = tone === "teal" ? "bg-teal-400/20 text-teal-200" : "bg-white/10 text-white/70";

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.5 }}
      className={`rounded-2xl border bg-gradient-to-br p-7 ${accent}`}
    >
      <div className="flex items-center gap-3 mb-6">
        <span className={`w-10 h-10 rounded-xl flex items-center justify-center ${iconBg}`}>
          {icon}
        </span>
        <p className="text-[11px] uppercase tracking-[0.18em] text-white/70 font-semibold">
          {eyebrow}
        </p>
      </div>
      <ul className="space-y-4">
        {items.map((it) => (
          <li key={it.title}>
            <p className="text-base font-semibold text-white/95 mb-1">{it.title}</p>
            <p className="text-sm text-white/60 leading-relaxed">{it.body}</p>
          </li>
        ))}
      </ul>
    </motion.div>
  );
}
