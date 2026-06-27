"use client";

import { motion } from "motion/react";
import { calibrationRows } from "../../_lib/mockData";

export function CalibrationDashboard() {
  return (
    <div className="w-full bg-white/[0.025] border border-white/10 rounded-2xl p-6 shadow-2xl">
      <div className="flex items-center justify-between mb-5">
        <div>
          <p className="text-[10px] uppercase tracking-wider text-white/40 mb-1">
            Calibration · trailing 12 months · Halcyon Apparel
          </p>
          <p className="text-white/90 font-medium">
            Recommendation accuracy by channel · confidence next run
          </p>
        </div>
        <span className="text-[10px] text-rose-300/80 font-mono px-2 py-1 bg-rose-500/10 rounded">
          Phase 4
        </span>
      </div>

      <div className="rounded-lg bg-[#0a162e]/60 border border-white/5 overflow-hidden">
        <table className="w-full text-xs">
          <thead className="bg-white/[0.025] text-white/40 text-[10px] uppercase tracking-wider">
            <tr>
              <th className="text-left px-4 py-2.5 font-medium">Channel</th>
              <th className="text-right px-3 py-2.5 font-medium">Suggestions</th>
              <th className="text-right px-3 py-2.5 font-medium">Predicted</th>
              <th className="text-right px-3 py-2.5 font-medium">Actual</th>
              <th className="text-center px-3 py-2.5 font-medium">Accuracy</th>
              <th className="text-right px-3 py-2.5 font-medium">Next confidence</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {calibrationRows.map((r, i) => {
              const good = r.accuracy >= 0.9;
              const ok = r.accuracy >= 0.8;
              return (
                <motion.tr
                  key={r.channel}
                  initial={{ opacity: 0, x: -8 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true, margin: "-50px" }}
                  transition={{ duration: 0.4, delay: i * 0.1 }}
                >
                  <td className="px-4 py-3 text-white/90 font-medium">{r.channel}</td>
                  <td className="px-3 py-3 text-right text-white/65 font-mono tabular-nums">{r.suggestions}</td>
                  <td className="px-3 py-3 text-right text-white/75 font-mono tabular-nums">{r.predicted}</td>
                  <td className="px-3 py-3 text-right text-white/75 font-mono tabular-nums">{r.actual}</td>
                  <td className="px-3 py-3">
                    <div className="flex items-center gap-2 justify-center">
                      <div className="w-16 h-1.5 bg-white/10 rounded overflow-hidden">
                        <motion.div
                          initial={{ scaleX: 0 }}
                          whileInView={{ scaleX: r.accuracy }}
                          viewport={{ once: true }}
                          transition={{ duration: 0.7, delay: 0.3 + i * 0.1 }}
                          style={{ originX: 0 }}
                          className={`h-full rounded ${
                            good ? "bg-emerald-400" : ok ? "bg-teal-400" : "bg-rose-400"
                          }`}
                        />
                      </div>
                      <span className={`text-[10px] font-mono tabular-nums ${
                        good ? "text-emerald-300" : ok ? "text-teal-300" : "text-rose-300"
                      }`}>
                        {Math.round(r.accuracy * 100)}%
                      </span>
                    </div>
                  </td>
                  <td className={`px-3 py-3 text-right text-xs font-mono font-semibold ${
                    r.nextConfidence.startsWith("+") ? "text-emerald-300" : "text-rose-300"
                  }`}>
                    {r.nextConfidence}
                  </td>
                </motion.tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="mt-5 px-4 py-3 rounded-lg bg-white/[0.025] border border-white/10 text-[11px] text-white/55 leading-relaxed">
        <span className="font-semibold text-white/85">TikTok confidence downweighted 24%.</span>{" "}
        The tool&apos;s own track record shows TikTok suggestions overshooting predicted
        impact by 69% on average. Confidence interval widens accordingly on next run.
        Visible to client. Auditable.
      </div>
    </div>
  );
}
