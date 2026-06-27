"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform, useReducedMotion } from "motion/react";

type Props = {
  number: number | string;
  label: string;
  months: string;
  // Position in the 33-month arc, 0..1
  arcStart: number;
  arcEnd: number;
};

export function PhaseRibbon({ number, label, months, arcStart, arcEnd }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const reduced = useReducedMotion();
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "end start"],
  });

  const sectionFill = useTransform(scrollYProgress, [0, 0.5, 1], [0, 1, 1]);
  const widthMV = useTransform(
    sectionFill,
    (v) => `${(arcEnd - arcStart) * 100 * v}%`,
  );
  const staticWidth = `${(arcEnd - arcStart) * 100}%`;

  return (
    <div ref={ref} className="sticky top-3 z-30 mb-10 md:mb-12">
      <div className="mx-auto max-w-6xl">
        <div className="bg-[#0f1e3d]/90 backdrop-blur-md border border-white/10 rounded-2xl px-5 py-3.5 flex flex-col md:flex-row md:items-center gap-3 md:gap-6 shadow-2xl">
          <div className="flex items-center gap-3 md:gap-4 flex-shrink-0">
            <span className="inline-flex items-center justify-center w-9 h-9 rounded-full bg-teal-400 text-[#0f1e3d] font-bold text-sm">
              {number}
            </span>
            <div>
              <p className="text-[10px] uppercase tracking-[0.18em] text-teal-300/80 leading-none">
                {label}
              </p>
              <p className="text-xs text-white/70 mt-0.5 leading-none">{months}</p>
            </div>
          </div>

          <div className="flex-1 md:ml-4">
            <div className="flex items-center justify-between text-[10px] uppercase tracking-wider text-white/40 mb-1.5">
              <span>Month 0</span>
              <span>Month 33+</span>
            </div>
            <div className="relative h-1.5 rounded-full bg-white/10 overflow-hidden">
              <div
                className="absolute top-0 bottom-0 bg-white/15 rounded-full"
                style={{ left: `${arcStart * 100}%`, width: staticWidth }}
              />
              <motion.div
                className="absolute top-0 bottom-0 bg-teal-400 rounded-full"
                style={{
                  left: `${arcStart * 100}%`,
                  width: reduced ? staticWidth : widthMV,
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
