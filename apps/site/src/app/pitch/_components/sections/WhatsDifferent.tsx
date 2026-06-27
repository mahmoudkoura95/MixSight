"use client";

import { motion } from "motion/react";
import { differentiators } from "../../_lib/content";
import { DisagreementBar } from "../mockups/DisagreementBar";
import { DefenseKitMini } from "../mockups/DefenseKitMini";
import { OptionsNotRecommendations } from "../mockups/OptionsNotRecommendations";
import { MultiMarketMap } from "../mockups/MultiMarketMap";
import { FreshnessUXSplit } from "../mockups/FreshnessUXSplit";
import { PlanChangeTimeline } from "../mockups/PlanChangeTimeline";
import { CalibrationGrowingChart } from "../mockups/CalibrationGrowingChart";

const registry: Record<string, React.ComponentType> = {
  DisagreementBar,
  DefenseKitMini,
  OptionsNotRecommendations,
  MultiMarketMap,
  FreshnessUXSplit,
  PlanChangeTimeline,
  CalibrationGrowingChart,
};

export function WhatsDifferent() {
  return (
    <section
      id="different"
      className="relative py-28 md:py-36 px-4 sm:px-6 lg:px-8 border-t border-white/5 scroll-mt-16 bg-gradient-to-b from-transparent via-white/[0.02] to-transparent"
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
            What&apos;s different
          </p>
          <h2 className="text-4xl md:text-5xl font-bold tracking-tight mb-5">
            Seven things we own.
          </h2>
          <p className="text-lg text-white/60 max-w-2xl mx-auto leading-relaxed">
            Not &quot;the first triangulation platform.&quot; Not &quot;another MMM
            tool.&quot; We win on workflow depth and the evidence the AM actually
            walks into the room with.
          </p>
        </motion.div>

        <div className="space-y-16 md:space-y-24">
          {differentiators.map((d, i) => {
            const Mock = registry[d.mockup] ?? null;
            const flipped = i % 2 === 1;
            return (
              <motion.div
                key={d.id}
                initial={{ opacity: 0, y: 32 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-80px" }}
                transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
                className={`grid md:grid-cols-2 gap-8 md:gap-12 items-center ${
                  flipped ? "md:[&>*:first-child]:order-2" : ""
                }`}
              >
                <div>
                  <p className="text-[10px] uppercase tracking-[0.18em] text-teal-300/70 font-mono mb-3">
                    {String(i + 1).padStart(2, "0")} · {d.cite}
                  </p>
                  <h3 className="text-2xl md:text-3xl font-semibold tracking-tight mb-4 leading-tight">
                    {d.title}
                  </h3>
                  <p className="text-white/65 leading-relaxed">{d.body}</p>
                </div>
                <div>
                  {Mock ? <Mock /> : <div className="bg-white/5 rounded-xl h-44" />}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
