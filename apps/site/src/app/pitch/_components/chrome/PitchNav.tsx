"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { navSections } from "../../_lib/content";

export function PitchNav() {
  const [activeId, setActiveId] = useState<string>("top");
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 100);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setActiveId(entry.target.id);
          }
        });
      },
      { rootMargin: "-40% 0px -50% 0px", threshold: 0 },
    );
    navSections.forEach((s) => {
      const el = document.getElementById(s.id);
      if (el) observer.observe(el);
    });

    return () => {
      window.removeEventListener("scroll", onScroll);
      observer.disconnect();
    };
  }, []);

  return (
    <AnimatePresence>
      {scrolled && (
        <motion.nav
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -12 }}
          transition={{ duration: 0.25 }}
          className="fixed top-3 left-1/2 -translate-x-1/2 z-50 hidden md:flex items-center gap-1 bg-[#0f1e3d]/85 backdrop-blur-md border border-white/10 rounded-full px-2.5 py-1.5 shadow-2xl"
          aria-label="Pitch navigation"
        >
          {navSections.map((s) => (
            <a
              key={s.id}
              href={`#${s.id}`}
              className={`relative px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${
                activeId === s.id
                  ? "text-[#0f1e3d]"
                  : "text-white/65 hover:text-white"
              }`}
            >
              {activeId === s.id && (
                <motion.span
                  layoutId="nav-active"
                  className="absolute inset-0 bg-teal-300 rounded-full"
                  transition={{ type: "spring", stiffness: 380, damping: 30 }}
                />
              )}
              <span className="relative z-10">{s.label}</span>
            </a>
          ))}
        </motion.nav>
      )}
    </AnimatePresence>
  );
}
