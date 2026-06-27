import type { Metadata } from "next";
import Link from "next/link";
import { Check, ChevronRight } from "lucide-react";
import { Nav } from "@/components/nav";
import { Footer } from "@/components/footer";

export const metadata: Metadata = {
  title: "Pricing",
  description:
    "Transparent pricing for performance agencies. Starter at $599/mo through Enterprise custom. Annual prepay saves 15%.",
};

type Tier = {
  name: string;
  price: number | null;
  description: string;
  seats: string;
  workspaces: string;
  highlight: boolean;
  features: string[];
  overages: string;
  cta: string;
  topic: string;
};

const tiers: Tier[] = [
  {
    name: "Starter",
    price: 599,
    description: "For agencies starting to systematize their pacing workflow.",
    seats: "2 seats",
    workspaces: "3 client workspaces",
    highlight: false,
    features: [
      "Single-market clients only",
      "4 connectors (Meta, Google Ads, GA4, TikTok)",
      "Plan templates (no AI parser)",
      "Weekly pacing snapshot",
      "Within-channel reallocation suggestions",
      "Static defense kit",
      "48-hour email support (business hours)",
    ],
    overages: "$50/seat · $99/workspace",
    cta: "Get started",
    topic: "pricing-starter",
  },
  {
    name: "Growth",
    price: 1499,
    description: "For agencies running multi-market, multi-channel campaigns.",
    seats: "5 seats",
    workspaces: "10 client workspaces",
    highlight: true,
    features: [
      "Multi-market clients",
      "All 4 connectors",
      "AI plan parser (Claude-powered)",
      "Full reallocation engine (all scopes)",
      "Editable defense kit with PDF export",
      "Evidence column (platform + GA4 inline)",
      "BYOK Anthropic API key option",
      "Logo + colors white-label on in-app and PDF",
      "Same-day email support",
    ],
    overages: "$40/seat · $79/workspace",
    cta: "Get started",
    topic: "pricing-growth",
  },
  {
    name: "Agency",
    price: 3999,
    description: "For agencies that need full white-label and priority access.",
    seats: "15 seats",
    workspaces: "30 client workspaces",
    highlight: false,
    features: [
      "Everything in Growth",
      "Custom domain (insights.youragency.com)",
      "Branded email-from for scheduled reports",
      "Branded client portal route",
      "“Powered by MixSight” footer toggle",
      "Priority support — dedicated Slack channel",
      "White-label setup assistance",
    ],
    overages: "$30/seat · $59/workspace",
    cta: "Get started",
    topic: "pricing-agency",
  },
  {
    name: "Enterprise",
    price: null,
    description: "Custom seat and workspace caps, SLA, SSO, and data residency.",
    seats: "Custom",
    workspaces: "Custom",
    highlight: false,
    features: [
      "Everything in Agency",
      "Custom legal entity for billing",
      "Data residency options (US / EU)",
      "Custom SAML SSO",
      "Audit log export",
      "Dedicated SLA",
    ],
    overages: "Custom",
    cta: "Contact us",
    topic: "enterprise",
  },
];

const faqs = [
  {
    q: "What counts as a client workspace?",
    a: "One client workspace = one brand or business entity you’re managing media for. Each client can have multiple markets within a single workspace at no extra charge.",
  },
  {
    q: "What is the 30-day pilot?",
    a: "All new accounts start with a 30-day pilot period — no credit card required upfront. At day 30, if MixSight isn’t saving your team real time, we part on good terms.",
  },
  {
    q: "What is BYOK?",
    a: "Bring Your Own Key. Growth and above can connect their own Anthropic API key for AI-powered features (plan parser, drift explanations, defense kit narrative). When BYOK is active, we apply a $200/workspace/month credit to your invoice.",
  },
  {
    q: "How does the annual prepay discount work?",
    a: "Pay 12 months upfront and get 15% off your total. Applied at checkout. Mixing monthly and annual workspaces is not supported.",
  },
  {
    q: "Can I change tiers?",
    a: "Yes, any time. Upgrades take effect immediately; downgrades take effect at the next billing cycle. We prorate upgrades.",
  },
  {
    q: "What happens if I cancel?",
    a: "30-day grace period from cancellation. Your data is preserved and reactivation is one click. At day 30, all customer data is hard-deleted. During the grace period you can download a full export of all your data.",
  },
];

export default function PricingPage() {
  return (
    <>
      <Nav />
      <main id="main">
        <section className="pt-20 pb-14 px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl sm:text-5xl font-bold text-slate-900 mb-4">
            Pricing
          </h1>
          <p className="text-xl text-slate-600 max-w-2xl mx-auto mb-6">
            Plans scale with your roster. Seats and workspaces as overages —
            pay for what you use.
          </p>
          <p className="text-sm text-teal-600 font-medium">
            Annual prepay: 15% discount on all tiers
          </p>
        </section>

        <section className="pb-24 px-4 sm:px-6 lg:px-8">
          <div className="max-w-6xl mx-auto grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {tiers.map((tier) => {
              const isEnterprise = tier.price === null;
              return (
                <div
                  key={tier.name}
                  className={`relative rounded-2xl p-6 flex flex-col ${
                    tier.highlight
                      ? "bg-teal-600 text-white ring-2 ring-teal-600 shadow-lg shadow-teal-600/20"
                      : "bg-white border border-slate-200"
                  }`}
                >
                  {tier.highlight && (
                    <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                      <span className="bg-amber-400 text-amber-900 text-xs font-semibold px-3 py-1 rounded-full whitespace-nowrap">
                        Most popular
                      </span>
                    </div>
                  )}
                  <div className="mb-6">
                    <h2
                      className={`text-sm font-semibold uppercase tracking-wide mb-1 ${
                        tier.highlight ? "text-teal-100" : "text-slate-500"
                      }`}
                    >
                      {tier.name}
                    </h2>
                    <div className="flex items-baseline gap-1 mb-2">
                      {!isEnterprise ? (
                        <>
                          <span
                            className={`text-4xl font-bold ${
                              tier.highlight ? "text-white" : "text-slate-900"
                            }`}
                          >
                            ${(tier.price as number).toLocaleString()}
                          </span>
                          <span
                            className={`text-sm ${
                              tier.highlight ? "text-teal-100" : "text-slate-500"
                            }`}
                          >
                            /mo
                          </span>
                        </>
                      ) : (
                        <span className="text-3xl font-bold text-slate-900">
                          Custom
                        </span>
                      )}
                    </div>
                    <p
                      className={`text-sm leading-relaxed ${
                        tier.highlight ? "text-teal-50" : "text-slate-600"
                      }`}
                    >
                      {tier.description}
                    </p>
                  </div>

                  <div
                    className={`text-xs mb-4 pb-4 border-b ${
                      tier.highlight
                        ? "text-teal-100 border-teal-500"
                        : "text-slate-500 border-slate-100"
                    }`}
                  >
                    <span className="font-medium">{tier.seats}</span> ·{" "}
                    <span className="font-medium">{tier.workspaces}</span>
                  </div>

                  <ul className="space-y-2.5 mb-8 flex-1">
                    {tier.features.map((feature) => (
                      <li key={feature} className="flex items-start gap-2.5">
                        <Check
                          className={`w-4 h-4 flex-shrink-0 mt-0.5 ${
                            tier.highlight ? "text-teal-100" : "text-teal-500"
                          }`}
                          aria-hidden="true"
                        />
                        <span
                          className={`text-sm ${
                            tier.highlight ? "text-teal-50" : "text-slate-600"
                          }`}
                        >
                          {feature}
                        </span>
                      </li>
                    ))}
                  </ul>

                  <div
                    className={`text-xs mb-4 ${
                      tier.highlight ? "text-teal-100" : "text-slate-400"
                    }`}
                  >
                    Overage: {tier.overages}
                  </div>

                  <Link
                    href={`/contact/?topic=${tier.topic}`}
                    className={`inline-flex items-center justify-center gap-2 w-full px-4 py-2.5 font-medium text-sm rounded-lg transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 ${
                      tier.highlight
                        ? "bg-white text-teal-600 hover:bg-teal-50 focus-visible:ring-teal-300 focus-visible:ring-offset-teal-600"
                        : "bg-teal-600 text-white hover:bg-teal-700 focus-visible:ring-teal-500"
                    }`}
                  >
                    {tier.cta}
                    <ChevronRight className="w-3.5 h-3.5" aria-hidden="true" />
                  </Link>
                </div>
              );
            })}
          </div>
        </section>

        <section className="py-12 px-4 sm:px-6 lg:px-8 bg-slate-50">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-xl font-bold text-slate-900 mb-3">
              Bring your own Anthropic API key
            </h2>
            <p className="text-slate-600 text-sm leading-relaxed mb-4">
              Growth, Agency, and Enterprise tiers can configure a
              per-workspace Anthropic API key. When BYOK is active, all AI
              generation calls use your key — we never see your token volume.
              We apply a{" "}
              <span className="font-medium text-slate-900">
                $200/workspace/month credit
              </span>{" "}
              to your next invoice, automatically. Per-workspace generation
              counts are still visible in your workspace dashboard.
            </p>
            <p className="text-xs text-slate-400">
              BYOK does not affect seat or workspace limits. Quota counts no
              longer apply when BYOK is active.
            </p>
          </div>
        </section>

        <section className="py-20 px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-2xl font-bold text-slate-900 mb-10 text-center">
              Frequently asked questions
            </h2>
            <div className="space-y-6">
              {faqs.map(({ q, a }) => (
                <div key={q} className="border-b border-slate-200 pb-6">
                  <h3 className="font-semibold text-slate-900 mb-2">{q}</h3>
                  <p className="text-sm text-slate-600 leading-relaxed">{a}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section className="py-16 px-4 sm:px-6 lg:px-8 bg-slate-50">
          <div className="max-w-xl mx-auto text-center">
            <h2 className="text-2xl font-bold text-slate-900 mb-3">
              Ready to start?
            </h2>
            <p className="text-slate-600 mb-8">
              All plans start with a 30-day pilot. No credit card required.
            </p>
            <Link
              href="/contact/?topic=early-access"
              className="inline-flex items-center gap-2 px-6 py-3 bg-teal-600 hover:bg-teal-700 text-white font-medium rounded-lg transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 focus-visible:ring-offset-2"
            >
              Request early access
              <ChevronRight className="w-4 h-4" aria-hidden="true" />
            </Link>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
