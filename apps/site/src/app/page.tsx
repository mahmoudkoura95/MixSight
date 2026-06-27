import Link from "next/link";
import {
  BarChart3,
  Shield,
  ArrowUpDown,
  FileText,
  Clock,
  TrendingUp,
  Users,
  ChevronRight,
  Check,
} from "lucide-react";
import { Nav } from "@/components/nav";
import { Footer } from "@/components/footer";

const problems = [
  {
    icon: Clock,
    title: "Four hours in spreadsheets",
    body: "Pulling numbers from Meta, Google, TikTok, GA4. Building the pacing table. Checking if the plan still makes sense. All before you touch the client.",
  },
  {
    icon: BarChart3,
    title: "Platform vs. analytics mismatches",
    body: "Meta says 340 conversions. GA4 says 218. Which number do you tell the client? The answer matters — so does your methodology for answering it.",
  },
  {
    icon: FileText,
    title: "No defensible one-pager",
    body: "The 11am client call is in 30 minutes. You have a tab full of pivot tables and nothing you'd comfortably share.",
  },
];

const features = [
  {
    icon: BarChart3,
    title: "Weekly pacing snapshot",
    body: "Automated status across every channel and market — spend drift, KPI drift, objective-aware thresholds. Green, amber, red, at a glance. Frozen Monday artifact with full audit trail.",
  },
  {
    icon: Shield,
    title: "Evidence column",
    body: "Platform numbers alongside GA4 analytics truth, inline on every pacing row. See the gap, understand the methodology, explain it to a client without opening four tabs.",
  },
  {
    icon: ArrowUpDown,
    title: "Reallocation options",
    body: "Three ranked suggestions, evidence-backed, respecting your taxonomy and budget constraints. Options with confidence — never “we recommend.” Your call, with better information.",
  },
  {
    icon: FileText,
    title: "Defense kit in 30 minutes",
    body: "Branded one-pager generated from your pacing data. Editable narrative, structural pacing table, selected reallocation rationale. PDF-ready. Send it before the call.",
  },
  {
    icon: TrendingUp,
    title: "Multi-market, multi-currency",
    body: "Per-market pacing in local currency, cross-market efficiency in reporting currency. FX updated daily. Built for agencies running clients across multiple geographies from day one.",
  },
  {
    icon: Users,
    title: "Built for agencies",
    body: "Onboard a new client in 12 minutes once connectors are wired. Organization-level OAuth — connect Meta Business Manager once, map ad accounts per client. Role-based access for your team.",
  },
];

const icpPoints = [
  "At least one client running across Meta + Google + GA4",
  "You care about measurement methodology, not just dashboards",
  "The founder or head-of-paid is the buyer and the primary user",
  "You’re US, UK, or EU-based and want a tool that speaks your workflow",
];

const designPartnerPerks = [
  "Agency-tier feature set ($3,999/mo retail value), free",
  "Locked-in $999/month on 12-month commitment at launch",
  "White-label setup assistance, custom domain, branding",
  "Weekly direct access to the founder",
];

const sampleRows = [
  {
    channel: "Meta — Prospecting",
    planned: "$48,500",
    actual: "$51,230",
    drift: "+5.6%",
    driftPositive: true,
    evidence: "Platform / GA4",
    status: "on-plan",
    statusClass: "bg-emerald-100 text-emerald-700",
  },
  {
    channel: "Google Search",
    planned: "$32,000",
    actual: "$24,800",
    drift: "−22.5%",
    driftPositive: false,
    evidence: "Platform / GA4",
    status: "critical",
    statusClass: "bg-red-100 text-red-700",
  },
  {
    channel: "TikTok — Video",
    planned: "$18,000",
    actual: "$19,400",
    drift: "+7.8%",
    driftPositive: true,
    evidence: "Platform",
    status: "amber",
    statusClass: "bg-amber-100 text-amber-700",
  },
  {
    channel: "Meta — Remarketing",
    planned: "$22,000",
    actual: "$21,900",
    drift: "−0.5%",
    driftPositive: true,
    evidence: "Platform / GA4",
    status: "on-plan",
    statusClass: "bg-emerald-100 text-emerald-700",
  },
];

export default function HomePage() {
  return (
    <>
      <Nav />
      <main id="main">
        {/* Hero */}
        <section className="pt-20 pb-20 px-4 sm:px-6 lg:px-8">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-teal-50 rounded-full mb-8">
              <span className="w-2 h-2 bg-teal-500 rounded-full" />
              <span className="text-xs font-medium text-teal-700">
                Now accepting design partners — Agency-tier access, free
              </span>
            </div>
            <h1 className="text-5xl sm:text-6xl font-bold text-slate-900 tracking-tight leading-[1.1] mb-6">
              Know where every dollar
              <br />
              <span className="text-teal-600">stands.</span>
            </h1>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed mb-10">
              MixSight turns Monday morning media review from four hours of
              spreadsheets into a thirty-minute workflow — with a
              defense-ready one-pager at the end.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/contact/?topic=early-access"
                className="inline-flex items-center gap-2 px-6 py-3 bg-teal-600 hover:bg-teal-700 text-white font-medium rounded-lg transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 focus-visible:ring-offset-2"
              >
                Request early access
                <ChevronRight className="w-4 h-4" aria-hidden="true" />
              </Link>
              <Link
                href="/pricing/"
                className="inline-flex items-center gap-2 px-6 py-3 bg-white border border-slate-300 hover:border-slate-400 text-slate-700 font-medium rounded-lg transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 focus-visible:ring-offset-2"
              >
                See pricing
              </Link>
            </div>
          </div>
        </section>

        {/* Product preview */}
        <section className="pb-24 px-4 sm:px-6 lg:px-8">
          <div className="max-w-5xl mx-auto">
            <div className="bg-slate-50 border border-slate-200 rounded-2xl p-6 sm:p-8">
              <div className="mb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                <div>
                  <p className="text-xs text-slate-400 mb-1">
                    Week ending May 11, 2026 — Brand X
                  </p>
                  <p className="text-sm font-medium text-slate-900">
                    4 markets · 12 channels · Net pacing +6.3% vs plan
                  </p>
                </div>
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-red-50 text-red-700 rounded">
                    2 critical
                  </span>
                  <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-amber-50 text-amber-700 rounded">
                    3 amber
                  </span>
                  <span className="inline-flex items-center px-2 py-1 text-xs font-medium bg-emerald-50 text-emerald-700 rounded">
                    7 on-plan
                  </span>
                </div>
              </div>
              <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-200 bg-slate-50">
                      <th className="text-left px-4 py-2.5 text-xs font-medium text-slate-500">
                        Channel
                      </th>
                      <th className="text-right px-4 py-2.5 text-xs font-medium text-slate-500">
                        Planned
                      </th>
                      <th className="text-right px-4 py-2.5 text-xs font-medium text-slate-500">
                        Actual
                      </th>
                      <th className="text-right px-4 py-2.5 text-xs font-medium text-slate-500">
                        Drift
                      </th>
                      <th className="text-left px-4 py-2.5 text-xs font-medium text-slate-500">
                        Evidence
                      </th>
                      <th className="text-center px-4 py-2.5 text-xs font-medium text-slate-500">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {sampleRows.map((row) => (
                      <tr key={row.channel} className="hover:bg-slate-50">
                        <td className="px-4 py-3 font-medium text-slate-900 whitespace-nowrap">
                          {row.channel}
                        </td>
                        <td className="px-4 py-3 text-right text-slate-600">
                          {row.planned}
                        </td>
                        <td className="px-4 py-3 text-right text-slate-900 font-medium">
                          {row.actual}
                        </td>
                        <td
                          className={`px-4 py-3 text-right font-medium ${
                            row.driftPositive ? "text-slate-600" : "text-red-600"
                          }`}
                        >
                          {row.drift}
                        </td>
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-1">
                            <span
                              className="w-3 h-3 rounded-full bg-teal-300"
                              aria-hidden="true"
                            />
                            <span
                              className="w-3 h-3 rounded-full bg-teal-600"
                              aria-hidden="true"
                            />
                            <span className="text-xs text-slate-400 ml-1">
                              {row.evidence}
                            </span>
                          </div>
                        </td>
                        <td className="px-4 py-3 text-center">
                          <span
                            className={`inline-flex px-2 py-0.5 text-xs font-medium rounded ${row.statusClass}`}
                          >
                            {row.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <p className="text-xs text-slate-400 mt-3 italic">
                Illustrative preview — your data, your branding.
              </p>
            </div>
          </div>
        </section>

        {/* Problem */}
        <section className="py-20 px-4 sm:px-6 lg:px-8 bg-slate-50">
          <div className="max-w-3xl mx-auto text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">
              Sound familiar?
            </h2>
            <p className="text-lg text-slate-600">
              If you run paid media across multiple platforms and markets, Monday
              morning has a routine.
            </p>
          </div>
          <div className="max-w-5xl mx-auto grid md:grid-cols-3 gap-6">
            {problems.map(({ icon: Icon, title, body }) => (
              <div
                key={title}
                className="bg-white rounded-xl p-6 border border-slate-200"
              >
                <div className="w-10 h-10 bg-teal-50 rounded-lg flex items-center justify-center mb-4">
                  <Icon className="w-5 h-5 text-teal-600" aria-hidden="true" />
                </div>
                <h3 className="font-semibold text-slate-900 mb-2">{title}</h3>
                <p className="text-sm text-slate-600 leading-relaxed">{body}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Features */}
        <section
          id="features"
          className="py-24 px-4 sm:px-6 lg:px-8 scroll-mt-16"
        >
          <div className="max-w-3xl mx-auto text-center mb-14">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">
              Everything you need for Monday morning
            </h2>
            <p className="text-lg text-slate-600">
              Built around the weekly review workflow — not the daily
              dashboard grind.
            </p>
          </div>
          <div className="max-w-5xl mx-auto grid md:grid-cols-2 gap-5">
            {features.map(({ icon: Icon, title, body }) => (
              <div
                key={title}
                className="flex gap-4 p-6 rounded-xl border border-slate-200 hover:border-teal-200 hover:bg-teal-50/30 transition-colors"
              >
                <div className="w-10 h-10 bg-teal-50 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Icon className="w-5 h-5 text-teal-600" aria-hidden="true" />
                </div>
                <div>
                  <h3 className="font-semibold text-slate-900 mb-1.5">
                    {title}
                  </h3>
                  <p className="text-sm text-slate-600 leading-relaxed">{body}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ICP / Design partner */}
        <section className="py-20 px-4 sm:px-6 lg:px-8 bg-slate-50">
          <div className="max-w-5xl mx-auto flex flex-col md:flex-row gap-10 items-start">
            <div className="flex-1">
              <h2 className="text-3xl font-bold text-slate-900 mb-4">
                Built for 5–25 person performance agencies
              </h2>
              <p className="text-slate-600 leading-relaxed mb-6">
                You’re running 3–8 active client engagements.
                Multi-market or aspiring multi-market. Currently living in
                Google Sheets or AgencyAnalytics, with real frustration about it.
              </p>
              <ul className="space-y-3">
                {icpPoints.map((point) => (
                  <li key={point} className="flex items-start gap-3">
                    <span
                      className="w-5 h-5 bg-teal-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
                      aria-hidden="true"
                    >
                      <span className="w-2 h-2 bg-teal-600 rounded-full" />
                    </span>
                    <span className="text-sm text-slate-700">{point}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="flex-1 bg-white rounded-2xl border border-slate-200 p-8 w-full">
              <p className="text-xs font-semibold text-teal-600 uppercase tracking-wide mb-2">
                Design partner program
              </p>
              <h3 className="text-xl font-bold text-slate-900 mb-3">
                Be our first design partner
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed mb-6">
                We’re onboarding one founding design partner now. You get
                Agency-tier access free through Phase 1, a locked-in $999/month
                rate afterward, and direct input on what gets built next.
              </p>
              <ul className="space-y-2 mb-6">
                {designPartnerPerks.map((item) => (
                  <li key={item} className="flex items-start gap-2">
                    <Check
                      className="w-4 h-4 text-teal-600 flex-shrink-0 mt-0.5"
                      aria-hidden="true"
                    />
                    <span className="text-sm text-slate-600">{item}</span>
                  </li>
                ))}
              </ul>
              <Link
                href="/contact/?topic=design-partner"
                className="inline-flex items-center gap-2 w-full justify-center px-5 py-3 bg-teal-600 hover:bg-teal-700 text-white font-medium rounded-lg transition-colors text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 focus-visible:ring-offset-2"
              >
                Apply to be a design partner
                <ChevronRight className="w-4 h-4" aria-hidden="true" />
              </Link>
            </div>
          </div>
        </section>

        {/* Final CTA */}
        <section className="py-24 px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl mx-auto text-center">
            <h2 className="text-4xl font-bold text-slate-900 mb-4">
              Stop rebuilding the pacing spreadsheet every Monday.
            </h2>
            <p className="text-lg text-slate-600 mb-10">
              Request early access. We respond within one business day.
            </p>
            <Link
              href="/contact/?topic=early-access"
              className="inline-flex items-center gap-2 px-8 py-4 bg-teal-600 hover:bg-teal-700 text-white font-medium rounded-lg transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 focus-visible:ring-offset-2"
            >
              Request early access
              <ChevronRight className="w-4 h-4" aria-hidden="true" />
            </Link>
            <p className="text-sm text-slate-400 mt-4">
              No credit card required · 30-day pilot.
            </p>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
