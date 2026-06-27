"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform, useReducedMotion } from "motion/react";
import Image from "next/image";
import { heroCopy } from "../../_lib/content";
import { ScrollCue } from "../chrome/ScrollCue";

export function Hero() {
  const ref = useRef<HTMLElement>(null);
  const reduced = useReducedMotion();
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start start", "end start"],
  });

  const titleY = useTransform(scrollYProgress, [0, 1], reduced ? [0, 0] : [0, -80]);
  const subhY = useTransform(scrollYProgress, [0, 1], reduced ? [0, 0] : [0, -40]);
  const orbX = useTransform(scrollYProgress, [0, 1], reduced ? [0, 0] : [0, -60]);
  const orbY = useTransform(scrollYProgress, [0, 1], reduced ? [0, 0] : [0, 100]);
  const orbX2 = useTransform(orbX, (v) => -v);
  const orbY2 = useTransform(orbY, (v) => -v);

  return (
    <section
      id="top"
      ref={ref}
      className="relative min-h-screen flex flex-col items-center justify-center overflow-hidden px-4 sm:px-6 lg:px-8"
    >
      {/* Background orbs */}
      <motion.div
        aria-hidden
        className="absolute -top-32 -right-32 w-[28rem] h-[28rem] rounded-full bg-teal-500/25 blur-3xl pointer-events-none"
        style={{ x: orbX, y: orbY }}
      />
      <motion.div
        aria-hidden
        className="absolute -bottom-32 -left-32 w-[34rem] h-[34rem] rounded-full bg-indigo-500/15 blur-3xl pointer-events-none"
        style={{ x: orbX2, y: orbY2 }}
      />

      {/* Grid texture */}
      <div
        aria-hidden
        className="absolute inset-0 opacity-[0.06] pointer-events-none"
        style={{
          backgroundImage:
            "linear-gradient(rgba(255,255,255,0.6) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.6) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
          maskImage:
            "radial-gradient(ellipse 70% 50% at center, black 30%, transparent 75%)",
        }}
      />

      <div className="relative z-10 w-full max-w-5xl mx-auto text-center pt-20 pb-24">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="inline-flex items-center gap-2 px-3 py-1 bg-white/5 border border-white/10 rounded-full mb-8"
        >
          <span className="w-1.5 h-1.5 bg-teal-400 rounded-full animate-pulse" />
          <span className="text-[11px] tracking-[0.18em] uppercase text-teal-300/80">
            {heroCopy.eyebrow}
          </span>
        </motion.div>

        <motion.h1
          style={{ y: titleY }}
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          className="text-5xl sm:text-6xl md:text-7xl font-bold tracking-tight leading-[1.05] mb-8"
        >
          {heroCopy.headline}
          <br />
          <span className="bg-gradient-to-r from-teal-300 via-teal-400 to-emerald-300 bg-clip-text text-transparent">
            {heroCopy.headlineAccent}
          </span>
        </motion.h1>

        <motion.p
          style={{ y: subhY }}
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.15, ease: [0.22, 1, 0.36, 1] }}
          className="text-lg sm:text-xl text-white/70 max-w-3xl mx-auto leading-relaxed mb-12"
        >
          {heroCopy.subhead}
        </motion.p>

        {/* Brand mark */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="inline-flex items-center gap-3 mb-16"
        >
          <span className="text-xs uppercase tracking-[0.2em] text-white/40">
            Brought to you by
          </span>
          <div className="bg-white rounded-md px-2.5 py-1.5">
            <Image src="/logo.png" alt="MixSight" width={100} height={26} priority />
          </div>
        </motion.div>

        <ScrollCue label={heroCopy.scrollCueLabel} />
      </div>

      {/* Faint roadmap arc bottom */}
      <motion.div
        initial={{ opacity: 0, scaleX: 0 }}
        animate={{ opacity: 1, scaleX: 1 }}
        transition={{ duration: 1.4, delay: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="absolute bottom-12 left-1/2 -translate-x-1/2 w-[88%] max-w-5xl origin-center"
      >
        <div className="h-px bg-gradient-to-r from-transparent via-teal-400/30 to-transparent" />
        <div className="mt-3 flex items-center justify-between text-[10px] uppercase tracking-[0.2em] text-white/30">
          <span>Phase 1</span>
          <span>Phase 2</span>
          <span>Phase 3</span>
          <span>Phase 4</span>
          <span>Beyond</span>
        </div>
      </motion.div>
    </section>
  );
}
