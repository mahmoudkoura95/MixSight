"use client";

import { motion, useReducedMotion } from "motion/react";
import { ChevronDown } from "lucide-react";

type Props = { label?: string };

export function ScrollCue({ label }: Props) {
  const reduced = useReducedMotion();

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 1, duration: 0.8 }}
      className="flex flex-col items-center gap-2 text-white/40 text-xs uppercase tracking-[0.18em]"
    >
      {label && <span>{label}</span>}
      <motion.div
        animate={reduced ? {} : { y: [0, 6, 0] }}
        transition={reduced ? {} : { duration: 1.6, repeat: Infinity, ease: "easeInOut" }}
      >
        <ChevronDown className="w-4 h-4" aria-hidden />
      </motion.div>
    </motion.div>
  );
}
