/**
 * Single-client single-market pacing view per §7.3 Phase 1a deliverable.
 *
 * Server component — fetches the §7.4 PacingSnapshot + lines + top-3
 * §7.10 ReallocationSuggestions from the FastAPI backend in parallel
 * and renders the table inline. Per `apps/web/CLAUDE.md`:
 *  - Server components by default — this is.
 *  - Taxonomy-driven filter bar contract acknowledged even though
 *    Phase 1a taxonomy is sparse (Phase 1b lights up CampaignLabelRule).
 *  - Empty-state catalog from §7.18 — inlined here for Week 3 single
 *    surface; the shared <EmptyState> in packages/shared lands when the
 *    second pacing surface needs it (current-week view, Phase 1c).
 *  - Reallocation framing: "options with evidence and confidence."
 *    Never "we recommend." Locked decision per CLAUDE.md.
 *
 * Out of scope for Week 3 (per CURRENT_PHASE.md):
 *  - Chart visualizations (table only — first chart triggers the
 *    library-choice §6.2 decision documented in DECISIONS.md).
 *  - Current-week settling treatment (§7.16 lands Phase 1c per the
 *    "cut-of-last-resort" callout).
 *  - Defense kit affordance (Week 4 — links here once shipped).
 */
import { ApiError, getJson } from "@/lib/api";

interface PacingSnapshotResponse {
  snapshot: {
    id: string;
    week_ending: string;
    generated_at: string | null;
    is_partial_week: boolean;
    allocation_mode: string;
  } | null;
  lines: Array<{
    id: string;
    plan_line_id: string;
    campaign_label: string | null;
    channel: string;
    objective_type: string;
    actual_spend_to_date: string | null;
    planned_spend_to_date: string | null;
    spend_drift_pct: string | null;
    actual_kpi_to_date: string | null;
    planned_kpi_to_date: string | null;
    kpi_drift_pct: string | null;
    status: string;
    labels: Record<string, unknown>;
  }>;
  currency: string;
  empty_state: string | null;
}

interface ReallocationResponse {
  snapshot_id: string | null;
  suggestions: Array<{
    id: string;
    donor_line_id: string;
    donor_campaign_label: string | null;
    receiver_line_id: string;
    receiver_campaign_label: string | null;
    proposed_amount_local: string;
    projected_delta: string | null;
    projected_delta_units: string | null;
    confidence: string | null;
    rationale_text: string | null;
    scope: string;
  }>;
  empty_state: string | null;
}

const _STATUS_STYLES: Record<string, string> = {
  green: "bg-emerald-500/10 text-emerald-300 border border-emerald-400/30",
  amber: "bg-amber-500/10 text-amber-300 border border-amber-400/30",
  red: "bg-rose-500/10 text-rose-300 border border-rose-400/30",
  critical: "bg-rose-600/20 text-rose-200 border border-rose-500/50",
  insufficient_data: "bg-white/5 text-white/40 border border-white/10",
};

function StatusBadge({ status }: { status: string }) {
  const cls = _STATUS_STYLES[status] ?? _STATUS_STYLES.insufficient_data;
  return (
    <span className={`px-2 py-0.5 rounded text-xs uppercase tracking-wider ${cls}`}>
      {status.replace("_", " ")}
    </span>
  );
}

function formatMoney(value: string | null, currency: string): string {
  if (value == null) return "—";
  const n = Number(value);
  if (Number.isNaN(n)) return value;
  return new Intl.NumberFormat("en-GB", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(n);
}

function formatPct(value: string | null): string {
  if (value == null) return "—";
  const n = Number(value);
  if (Number.isNaN(n)) return value;
  const sign = n > 0 ? "+" : "";
  return `${sign}${n.toFixed(1)}%`;
}

function EmptyState({ headline, body }: { headline: string; body: string }) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-lg p-8 text-center">
      <h2 className="text-lg font-semibold text-white/80 mb-2">{headline}</h2>
      <p className="text-sm text-white/50">{body}</p>
    </div>
  );
}

export default async function PacingPage(props: {
  params: Promise<{ clientId: string; marketId: string }>;
}) {
  const { clientId, marketId } = await props.params;

  let pacing: PacingSnapshotResponse;
  let reallocation: ReallocationResponse;
  try {
    [pacing, reallocation] = await Promise.all([
      getJson<PacingSnapshotResponse>(`/clients/${clientId}/markets/${marketId}/pacing`),
      getJson<ReallocationResponse>(
        `/clients/${clientId}/markets/${marketId}/reallocation-suggestions`,
      ),
    ]);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) {
      return (
        <main className="min-h-screen bg-[#0f1e3d] text-white p-8">
          <div className="max-w-4xl mx-auto">
            <EmptyState
              headline="Client or market not found"
              body="Either this client doesn't exist or your account doesn't have access. Contact your agency admin if you think this is wrong."
            />
          </div>
        </main>
      );
    }
    throw err;
  }

  const generatedAt = pacing.snapshot?.generated_at
    ? new Date(pacing.snapshot.generated_at).toLocaleString("en-GB", {
        timeZone: "Europe/London",
        dateStyle: "medium",
        timeStyle: "short",
      })
    : null;

  return (
    <main className="min-h-screen bg-[#0f1e3d] text-white px-6 py-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <header className="flex items-baseline justify-between border-b border-white/10 pb-4">
          <div>
            <h1 className="text-2xl font-semibold">Pacing snapshot</h1>
            <p className="text-sm text-white/50">
              Week ending {pacing.snapshot?.week_ending ?? "—"} · {pacing.currency}
            </p>
          </div>
          {generatedAt && (
            <p className="text-xs text-white/40">
              Data current as of {generatedAt} Europe/London.
              {/* §7.16 freshness stamp. Weekly snapshot only in Phase 1a;
                  current-week view + settling treatment lands Phase 1c. */}
            </p>
          )}
        </header>

        {pacing.snapshot?.is_partial_week && (
          <div className="bg-amber-500/10 border border-amber-400/30 text-amber-200 rounded-lg px-4 py-3 text-sm">
            Partial week — Plan covers less than a full Monday–Sunday. Drift
            numbers reflect a prorated planned-to-date. Full snapshot
            available next Monday.
          </div>
        )}

        {pacing.empty_state === "no_active_plan" ? (
          <EmptyState
            headline="No active plan for this week"
            body="Upload a plan via the template CSV upload (lands Week 4) or contact your agency admin. The pacing surface activates once a plan covers this week."
          />
        ) : pacing.empty_state === "no_spend_in_market" || pacing.lines.length === 0 ? (
          <EmptyState
            headline="No spend recorded yet"
            body="A plan exists for this week but no actuals have been uploaded. Drag-drop a Meta Ads Manager CSV on the upload area (next to the snapshot) and refresh."
          />
        ) : (
          <section className="bg-white/[0.03] border border-white/10 rounded-xl overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-white/5 text-white/60 text-xs uppercase tracking-wider">
                <tr>
                  <th className="px-4 py-3 text-left font-medium">Campaign</th>
                  <th className="px-4 py-3 text-left font-medium">Objective</th>
                  <th className="px-4 py-3 text-right font-medium">Spend (actual / plan)</th>
                  <th className="px-4 py-3 text-right font-medium">Spend drift</th>
                  <th className="px-4 py-3 text-right font-medium">KPI (actual / plan)</th>
                  <th className="px-4 py-3 text-right font-medium">KPI drift</th>
                  <th className="px-4 py-3 text-left font-medium">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {pacing.lines.map((ln) => (
                  <tr key={ln.id} className="hover:bg-white/[0.02]">
                    <td className="px-4 py-3">
                      <div className="font-medium text-white/90">
                        {ln.campaign_label ?? "—"}
                      </div>
                      <div className="text-xs text-white/40">
                        {ln.channel.toUpperCase()}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-white/70">{ln.objective_type}</td>
                    <td className="px-4 py-3 text-right tabular-nums">
                      <span className="text-white/90">
                        {formatMoney(ln.actual_spend_to_date, pacing.currency)}
                      </span>{" "}
                      <span className="text-white/40">/</span>{" "}
                      <span className="text-white/50">
                        {formatMoney(ln.planned_spend_to_date, pacing.currency)}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right tabular-nums">
                      {formatPct(ln.spend_drift_pct)}
                    </td>
                    <td className="px-4 py-3 text-right tabular-nums text-white/80">
                      {ln.actual_kpi_to_date ?? "—"} <span className="text-white/40">/</span>{" "}
                      {ln.planned_kpi_to_date ?? "—"}
                    </td>
                    <td className="px-4 py-3 text-right tabular-nums">
                      {formatPct(ln.kpi_drift_pct)}
                    </td>
                    <td className="px-4 py-3">
                      <StatusBadge status={ln.status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        )}

        <section>
          <h2 className="text-lg font-semibold mb-1">Reallocation options</h2>
          <p className="text-sm text-white/50 mb-4">
            Top {reallocation.suggestions.length} options with evidence and
            confidence. <span className="text-white/40">(Never &ldquo;we recommend&rdquo; — see §7.10.)</span>
          </p>
          {reallocation.suggestions.length === 0 ? (
            <EmptyState
              headline="No reallocation options this week"
              body={
                reallocation.empty_state === "insufficient_data"
                  ? "Most campaigns have under 14 days of actuals. Options surface once enough history accumulates — typically next week."
                  : "Every campaign is pacing on-target. No donor + receiver pairs to suggest."
              }
            />
          ) : (
            <ul className="space-y-3">
              {reallocation.suggestions.map((s) => (
                <li
                  key={s.id}
                  className="bg-white/[0.03] border border-white/10 rounded-lg p-4"
                >
                  <p className="text-sm text-white/90 mb-2">{s.rationale_text}</p>
                  <div className="flex gap-6 text-xs text-white/50">
                    <span>
                      Amount:{" "}
                      <span className="text-white/80 tabular-nums">
                        {formatMoney(s.proposed_amount_local, pacing.currency)}
                      </span>
                    </span>
                    <span>
                      Projected Δ:{" "}
                      <span className="text-white/80 tabular-nums">
                        {s.projected_delta ?? "—"} {s.projected_delta_units ?? ""}
                      </span>
                    </span>
                    <span>
                      Confidence:{" "}
                      <span className="text-white/80 tabular-nums">
                        {s.confidence ?? "—"}
                      </span>
                    </span>
                    <span className="text-white/40">Scope: {s.scope}</span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </main>
  );
}
