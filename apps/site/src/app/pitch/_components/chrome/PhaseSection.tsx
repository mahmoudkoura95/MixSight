"use client";

import { motion } from "motion/react";
import { PhaseRibbon } from "./PhaseRibbon";

type MockupSection = {
  mockup: string;
  title: string;
  cite: string;
  callouts: string[];
};

type PhaseData = {
  number: number | string;
  label: string;
  months: string;
  northStar: string;
  subhead: string;
  mockupSections: MockupSection[];
  wowMoments: string[];
};

type Props = {
  id: string;
  arcStart: number;
  arcEnd: number;
  data: PhaseData;
  registry: Record<string, React.ComponentType>;
  accent?: "teal" | "amber" | "indigo" | "rose";
};

const accentClasses = {
  teal: { eyebrow: "text-teal-300/80", dot: "bg-teal-400" },
  amber: { eyebrow: "text-amber-300/80", dot: "bg-amber-400" },
  indigo: { eyebrow: "text-indigo-300/80", dot: "bg-indigo-400" },
  rose: { eyebrow: "text-rose-300/80", dot: "bg-rose-400" },
};

export function PhaseSection({ id, arcStart, arcEnd, data, registry, accent = "teal" }: Props) {
  const a = accentClasses[accent];

  return (
    <section id={id} className="relative py-20 md:py-28 px-4 sm:px-6 lg:px-8 border-t border-white/5 scroll-mt-16">
      <div className="max-w-6xl mx-auto">
        <PhaseRibbon
          number={data.number}
          label={data.label}
          months={data.months}
          arcStart={arcStart}
          arcEnd={arcEnd}
        />

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.5 }}
          className="mb-16 md:mb-20 max-w-4xl"
        >
          <p className={`text-[11px] uppercase tracking-[0.2em] ${a.eyebrow} mb-3`}>
            North star · {data.label}
          </p>
          <h2 className="text-3xl md:text-5xl font-bold tracking-tight leading-tight mb-5">
            {data.northStar}
          </h2>
          <p className="text-base md:text-lg text-white/60 leading-relaxed">
            {data.subhead}
          </p>
        </motion.div>

        <div className="space-y-16 md:space-y-24">
          {data.mockupSections.map((ms, i) => {
            const Mock = registry[ms.mockup] ?? null;
            const flipped = i % 2 === 1;
            return (
              <div
                key={ms.mockup + i}
                className={`grid md:grid-cols-12 gap-8 md:gap-12 items-center`}
              >
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-80px" }}
                  transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                  className={`md:col-span-7 ${flipped ? "md:order-2" : ""}`}
                >
                  {Mock ? <Mock /> : <div className="h-64 bg-white/5 rounded-2xl" />}
                </motion.div>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-80px" }}
                  transition={{ duration: 0.6, delay: 0.12, ease: [0.22, 1, 0.36, 1] }}
                  className={`md:col-span-5 ${flipped ? "md:order-1" : ""}`}
                >
                  <p className="text-[10px] uppercase tracking-[0.18em] font-mono text-white/40 mb-3">
                    {ms.cite}
                  </p>
                  <h3 className="text-2xl md:text-3xl font-semibold tracking-tight leading-tight mb-5">
                    {ms.title}
                  </h3>
                  <ul className="space-y-2.5">
                    {ms.callouts.map((c) => (
                      <li key={c} className="flex items-start gap-2.5">
                        <span className={`mt-1.5 w-1.5 h-1.5 rounded-full ${a.dot} flex-shrink-0`} />
                        <span className="text-sm text-white/70 leading-relaxed">{c}</span>
                      </li>
                    ))}
                  </ul>
                </motion.div>
              </div>
            );
          })}
        </div>

        {/* Wow moments */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-80px" }}
          transition={{ duration: 0.6 }}
          className="mt-20 md:mt-28 rounded-2xl border border-white/10 bg-gradient-to-br from-white/[0.04] to-white/[0.01] p-7 md:p-10"
        >
          <p className={`text-[11px] uppercase tracking-[0.2em] ${a.eyebrow} mb-5`}>
            What an agency principal says when they see this
          </p>
          <ul className="space-y-4">
            {data.wowMoments.map((m, i) => (
              <motion.li
                key={m}
                initial={{ opacity: 0, x: -8 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.1 }}
                className="text-lg md:text-xl text-white/85 leading-relaxed font-medium"
              >
                {m}
              </motion.li>
            ))}
          </ul>
        </motion.div>
      </div>
    </section>
  );
}
