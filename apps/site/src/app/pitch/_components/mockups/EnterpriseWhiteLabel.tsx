"use client";

import { motion } from "motion/react";
import { Lock, ShieldCheck, Globe } from "lucide-react";

export function EnterpriseWhiteLabel() {
  return (
    <div className="w-full bg-white/[0.025] border border-white/10 rounded-2xl p-6 shadow-2xl">
      <div className="flex items-center justify-between mb-5">
        <div>
          <p className="text-[10px] uppercase tracking-wider text-white/40 mb-1">
            Layer 3 white-label · Enterprise tier
          </p>
          <p className="text-white/90 font-medium">
            Custom domain · custom legal entity · SAML SSO · data residency
          </p>
        </div>
        <span className="text-[10px] text-rose-300/80 font-mono px-2 py-1 bg-rose-500/10 rounded">
          Phase 4d
        </span>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-50px" }}
        transition={{ duration: 0.6 }}
        className="rounded-xl bg-white text-slate-800 shadow-[0_20px_50px_-12px_rgba(0,0,0,0.6)] overflow-hidden"
      >
        {/* Browser chrome */}
        <div className="bg-slate-100 px-3 py-2 flex items-center gap-2 border-b border-slate-200">
          <div className="flex gap-1.5">
            <span className="w-3 h-3 rounded-full bg-rose-400" />
            <span className="w-3 h-3 rounded-full bg-amber-400" />
            <span className="w-3 h-3 rounded-full bg-emerald-400" />
          </div>
          <div className="flex-1 ml-3 flex items-center gap-2 bg-white rounded px-3 py-1 text-[11px] text-slate-500 font-mono">
            <Lock className="w-3 h-3" aria-hidden />
            insights.lumenstudios.com
          </div>
          <span className="text-[10px] text-slate-400 font-mono">EU-WEST · GDPR</span>
        </div>

        {/* SSO panel */}
        <div className="px-8 py-10 flex flex-col items-center text-center">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-slate-800 to-slate-600 flex items-center justify-center text-white font-bold text-lg mb-4">
            LS
          </div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-400 mb-2">
            Lumen Studios · Client portal
          </p>
          <h4 className="text-xl font-semibold text-slate-900 mb-4">
            Sign in to continue
          </h4>

          <div className="w-full max-w-xs space-y-2.5">
            <button className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-slate-900 text-white text-sm hover:bg-slate-800 transition-colors">
              <ShieldCheck className="w-4 h-4" aria-hidden />
              Sign in with Okta SAML
            </button>
            <button className="w-full inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg border border-slate-300 text-slate-700 text-sm hover:bg-slate-50 transition-colors">
              <Globe className="w-4 h-4" aria-hidden />
              Sign in with Azure AD
            </button>
          </div>

          <p className="text-[10px] text-slate-400 mt-6">
            Powered by <span className="font-semibold text-slate-600">measurement infrastructure</span> · ISO 27001 · SOC 2 Type II
          </p>
        </div>
      </motion.div>

      <div className="mt-5 grid sm:grid-cols-3 gap-3 text-[11px]">
        <Pill icon={<ShieldCheck className="w-3.5 h-3.5" aria-hidden />} text="SAML SSO" />
        <Pill icon={<Globe className="w-3.5 h-3.5" aria-hidden />} text="EU / US residency" />
        <Pill icon={<Lock className="w-3.5 h-3.5" aria-hidden />} text="Custom legal entity" />
      </div>
    </div>
  );
}

function Pill({ icon, text }: { icon: React.ReactNode; text: string }) {
  return (
    <span className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/[0.025] border border-white/10 text-white/75">
      {icon}
      {text}
    </span>
  );
}
