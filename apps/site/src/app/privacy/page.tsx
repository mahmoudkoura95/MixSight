import type { Metadata } from "next";
import { Nav } from "@/components/nav";
import { Footer } from "@/components/footer";

export const metadata: Metadata = {
  title: "Privacy Policy",
  description:
    "MixSight privacy policy — how we collect, use, and protect your data, including advertising platform OAuth data and AI generation.",
};

export default function PrivacyPage() {
  return (
    <>
      <Nav />
      <main id="main" className="py-16 px-4 sm:px-6 lg:px-8">
        <article className="max-w-3xl mx-auto">
          <header className="mb-10">
            <h1 className="text-3xl font-bold text-slate-900 mb-2">
              Privacy Policy
            </h1>
            <p className="text-sm text-slate-500">Last updated: May 13, 2026</p>
          </header>

          <div className="space-y-8 text-sm text-slate-700 leading-relaxed">
            <section aria-labelledby="s1">
              <h2
                id="s1"
                className="text-lg font-semibold text-slate-900 mb-3"
              >
                1. About this policy
              </h2>
              <p>
                MixSight (“we,” “us,” or “our”) operates the platform available
                at <span className="font-medium">app.mixsight.ai</span> (the
                “Service”). This Privacy Policy explains what information we
                collect, how we use it, and your rights with respect to that
                information. By using the Service, you agree to the collection
                and use of information in accordance with this policy.
              </p>
              <p className="mt-3">
                MixSight is a paid media pacing and measurement platform for
                performance marketing agencies. We connect to advertising
                platforms (Meta, Google Ads, Google Analytics 4, and TikTok)
                via OAuth on your authorization, import campaign performance
                data, and present that data in a structured workflow to help
                agency teams manage and report on client media spend.
              </p>
            </section>

            <section aria-labelledby="s2">
              <h2
                id="s2"
                className="text-lg font-semibold text-slate-900 mb-3"
              >
                2. Information we collect
              </h2>

              <h3 className="font-medium text-slate-900 mb-2">
                2.1 Account and organization information
              </h3>
              <p>
                When you create a MixSight account, we collect your name, email
                address, and organization details. We use Clerk for
                authentication; their privacy policy governs their handling of
                authentication credentials.
              </p>

              <h3 className="font-medium text-slate-900 mt-4 mb-2">
                2.2 Advertising platform data (via OAuth)
              </h3>
              <p>
                With your explicit authorization via OAuth, we access
                advertising account data from the platforms you connect:
              </p>
              <ul className="mt-2 space-y-1 list-disc pl-5">
                <li>
                  <span className="font-medium">
                    Meta (Facebook/Instagram Ads):
                  </span>{" "}
                  campaign names, ad account IDs, spend, impressions, clicks,
                  conversions, and attribution data from accounts you authorize
                  via Meta Business Manager.
                </li>
                <li>
                  <span className="font-medium">Google Ads:</span> campaign
                  names, account IDs, spend, impressions, clicks, and
                  conversion data from accounts you authorize via Google MCC or
                  direct account access.
                </li>
                <li>
                  <span className="font-medium">
                    Google Analytics 4 (GA4):
                  </span>{" "}
                  sessions, conversions, and purchase revenue aggregated by
                  source/medium, from properties you authorize.
                </li>
                <li>
                  <span className="font-medium">TikTok Ads:</span> campaign
                  names, ad account IDs, spend, impressions, and engagement
                  data from accounts you authorize via TikTok Business Center.
                </li>
              </ul>
              <p className="mt-3">
                This data is imported at the campaign level, not at the
                individual user or consumer level. We do not access, store, or
                process any end-consumer personal data from your advertising
                audiences. All platform data access is governed by the
                respective platform’s terms of service and developer policies.
              </p>

              <h3 className="font-medium text-slate-900 mt-4 mb-2">
                2.3 Media plan data
              </h3>
              <p>
                You may upload or input media plan documents (Excel, CSV)
                containing budget allocations, campaign structures, and planned
                KPIs. This data is stored to provide the core pacing and
                measurement functionality.
              </p>

              <h3 className="font-medium text-slate-900 mt-4 mb-2">
                2.4 Usage data
              </h3>
              <p>
                We collect information about how you use the Service, including
                pages visited, features used, and actions taken (such as
                generating a defense kit or confirming a reallocation
                suggestion). This is used to improve the product and diagnose
                issues.
              </p>

              <h3 className="font-medium text-slate-900 mt-4 mb-2">
                2.5 OAuth tokens and API credentials
              </h3>
              <p>
                We store OAuth access tokens and refresh tokens for connected
                advertising platforms. These are encrypted at rest using
                industry-standard encryption (Fernet symmetric encryption with
                a rotating master key). We use these tokens solely to retrieve
                campaign performance data on your behalf per the pull schedules
                you configure.
              </p>
            </section>

            <section aria-labelledby="s3">
              <h2
                id="s3"
                className="text-lg font-semibold text-slate-900 mb-3"
              >
                3. How we use your information
              </h2>
              <p>We use the information we collect to:</p>
              <ul className="mt-2 space-y-1 list-disc pl-5">
                <li>
                  Provide the core MixSight service: pacing analysis,
                  reallocation suggestions, and defense-kit generation.
                </li>
                <li>
                  Retrieve advertising performance data from connected
                  platforms on your behalf, on the schedule you configure.
                </li>
                <li>
                  Generate AI-assisted content (drift explanations, defense kit
                  narratives) using the Anthropic API. We do not train
                  Anthropic models on your data. When you provide your own
                  Anthropic API key (BYOK), we do not see your token volume.
                </li>
                <li>
                  Send transactional communications: data freshness alerts,
                  connector health notifications, billing receipts.
                </li>
                <li>
                  Improve and debug the Service using aggregated, anonymized
                  usage signals.
                </li>
                <li>Comply with legal obligations.</li>
              </ul>
              <p className="mt-3">
                We do not sell your data. We do not share your advertising
                performance data, plan data, or client data with any third
                party except as necessary to provide the Service
                (infrastructure providers, authentication provider) or as
                required by law.
              </p>
              <p className="mt-3">
                We do not use your advertising platform data for cross-customer
                benchmarking or analytics without your explicit opt-in and only
                after applying differential privacy techniques that prevent
                reconstruction of individual contributions.
              </p>
            </section>

            <section aria-labelledby="s4">
              <h2
                id="s4"
                className="text-lg font-semibold text-slate-900 mb-3"
              >
                4. Data retention and deletion
              </h2>

              <h3 className="font-medium text-slate-900 mb-2">
                4.1 Active accounts
              </h3>
              <p>
                We retain your data for as long as your account is active. All
                advertising platform data is stored as campaign-level
                aggregates; we do not retain raw ad impressions or
                consumer-level events.
              </p>

              <h3 className="font-medium text-slate-900 mt-4 mb-2">
                4.2 Account cancellation
              </h3>
              <p>
                On cancellation, a 30-day grace period begins. During this
                period, your data is preserved and your account can be
                reactivated. At day 30, all customer-specific data is
                permanently deleted: plans, actuals, pacing snapshots,
                reallocation history, defense kits, and connector credentials.
                OAuth credentials (API tokens) are deleted immediately at
                cancellation, with no grace period, to prevent further data
                pulls.
              </p>
              <p className="mt-2">
                During the grace period, you can download a full export of all
                your data from{" "}
                <span className="font-medium">/settings/export</span>.
              </p>

              <h3 className="font-medium text-slate-900 mt-4 mb-2">
                4.3 Audit log retention
              </h3>
              <p>
                We retain audit log records for 7 years for compliance
                purposes. Upon account deletion, identifiers in the audit log
                are anonymized using a deterministic hash that cannot be
                reverse-engineered to identify the customer.
              </p>
            </section>

            <section aria-labelledby="s5">
              <h2
                id="s5"
                className="text-lg font-semibold text-slate-900 mb-3"
              >
                5. Security
              </h2>
              <p>We implement industry-standard security measures:</p>
              <ul className="mt-2 space-y-1 list-disc pl-5">
                <li>
                  OAuth tokens and API credentials encrypted at rest (Fernet
                  encryption, rotating key versions).
                </li>
                <li>All data in transit encrypted via TLS 1.2+.</li>
                <li>
                  Access controls: agency users only access their own
                  organization’s data; account managers only access assigned
                  clients.
                </li>
                <li>
                  Audit log of every data mutation for operational
                  accountability.
                </li>
                <li>
                  We do not store advertising platform passwords or two-factor
                  authentication credentials.
                </li>
              </ul>
              <p className="mt-3">
                No system is perfectly secure. If you believe a security
                incident has occurred, please contact us immediately at{" "}
                <a
                  href="mailto:security@mixsight.ai"
                  className="text-teal-600 hover:underline"
                >
                  security@mixsight.ai
                </a>
                .
              </p>
            </section>

            <section aria-labelledby="s6">
              <h2
                id="s6"
                className="text-lg font-semibold text-slate-900 mb-3"
              >
                6. Cookies and tracking
              </h2>
              <p>
                The MixSight application uses session cookies necessary for
                authentication and security. We do not use third-party
                advertising cookies or tracking pixels on the application. Our
                marketing website (mixsight.ai) may use analytics cookies to
                understand traffic sources; these are not connected to your
                MixSight account data.
              </p>
            </section>

            <section aria-labelledby="s7">
              <h2
                id="s7"
                className="text-lg font-semibold text-slate-900 mb-3"
              >
                7. Third-party services
              </h2>
              <p>We use the following third-party services to operate MixSight:</p>
              <ul className="mt-2 space-y-2 list-disc pl-5">
                <li>
                  <span className="font-medium">Clerk</span> — authentication
                  and user management.
                </li>
                <li>
                  <span className="font-medium">Anthropic</span> — AI content
                  generation (drift explanations, plan parsing, defense kit
                  narratives). We send campaign-level performance data and plan
                  context. We do not send consumer personal data.
                </li>
                <li>
                  <span className="font-medium">Stripe</span> — payment
                  processing and billing.
                </li>
                <li>
                  <span className="font-medium">Sentry</span> — error
                  monitoring. Error reports may include anonymized usage
                  context but do not include advertising platform data.
                </li>
              </ul>
              <p className="mt-3">
                Each third party operates under its own privacy policy. We
                select processors that meet our security and compliance
                requirements.
              </p>
            </section>

            <section aria-labelledby="s8">
              <h2
                id="s8"
                className="text-lg font-semibold text-slate-900 mb-3"
              >
                8. Your rights (GDPR and CCPA)
              </h2>
              <p>
                Depending on your jurisdiction, you may have the following
                rights with respect to your personal data:
              </p>
              <ul className="mt-2 space-y-1 list-disc pl-5">
                <li>
                  <span className="font-medium">Access:</span> Request a copy
                  of personal data we hold about you.
                </li>
                <li>
                  <span className="font-medium">Rectification:</span> Request
                  correction of inaccurate data.
                </li>
                <li>
                  <span className="font-medium">
                    Erasure (right to be forgotten):
                  </span>{" "}
                  Request deletion of your personal data. We will complete
                  erasure within 30 days and send acknowledgment within 48
                  hours of request.
                </li>
                <li>
                  <span className="font-medium">Portability:</span> Download
                  your data in machine-readable format via{" "}
                  <span className="font-medium">/settings/export</span>.
                </li>
                <li>
                  <span className="font-medium">Objection:</span> Object to
                  specific processing activities.
                </li>
              </ul>
              <p className="mt-3">
                To exercise any of these rights, contact us at{" "}
                <a
                  href="mailto:privacy@mixsight.ai"
                  className="text-teal-600 hover:underline"
                >
                  privacy@mixsight.ai
                </a>
                . We will respond within 30 days.
              </p>
            </section>

            <section aria-labelledby="s9">
              <h2
                id="s9"
                className="text-lg font-semibold text-slate-900 mb-3"
              >
                9. Advertising platform data — specific disclosures
              </h2>
              <p>
                Our use and transfer of information received from Google APIs
                to any other app adheres to{" "}
                <a
                  href="https://developers.google.com/terms/api-services-user-data-policy"
                  className="text-teal-600 hover:underline"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Google API Services User Data Policy
                </a>
                , including the Limited Use requirements.
              </p>
              <p className="mt-3">
                Specifically regarding data obtained from Google APIs:
              </p>
              <ul className="mt-2 space-y-1 list-disc pl-5">
                <li>
                  We use Google Ads and GA4 data solely to provide the MixSight
                  pacing and measurement service to the authorized account
                  holder.
                </li>
                <li>We do not use Google data to serve advertisements.</li>
                <li>
                  We do not allow humans to read Google user data unless the
                  user explicitly requests it for a support case, it is
                  necessary for security investigations, or it is required by
                  law.
                </li>
                <li>
                  We do not use Google data to train AI or ML models beyond
                  what is necessary to provide the Service.
                </li>
                <li>
                  We do not transfer Google data to third parties except as
                  necessary to provide the Service, and those parties are
                  under equivalent obligations.
                </li>
              </ul>
              <p className="mt-3">
                Our use of Meta Marketing API data is governed by the{" "}
                <a
                  href="https://developers.facebook.com/terms/"
                  className="text-teal-600 hover:underline"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Meta Platform Terms
                </a>{" "}
                and applicable data policies. Meta campaign data is used solely
                to provide the authorized user with pacing and measurement
                information for their own ad accounts.
              </p>
            </section>

            <section aria-labelledby="s10">
              <h2
                id="s10"
                className="text-lg font-semibold text-slate-900 mb-3"
              >
                10. Children’s privacy
              </h2>
              <p>
                MixSight is a B2B platform intended for business use only. We
                do not knowingly collect personal information from anyone under
                18 years of age.
              </p>
            </section>

            <section aria-labelledby="s11">
              <h2
                id="s11"
                className="text-lg font-semibold text-slate-900 mb-3"
              >
                11. Changes to this policy
              </h2>
              <p>
                We may update this Privacy Policy from time to time. We will
                notify you of material changes by email and by posting the
                updated policy with a new effective date. Continued use of the
                Service after changes take effect constitutes acceptance of the
                revised policy.
              </p>
            </section>

            <section aria-labelledby="s12">
              <h2
                id="s12"
                className="text-lg font-semibold text-slate-900 mb-3"
              >
                12. Contact
              </h2>
              <p>
                For privacy-related questions, data requests, or to report a
                concern:
              </p>
              <div className="mt-3 space-y-1">
                <p>
                  <span className="font-medium">Email:</span>{" "}
                  <a
                    href="mailto:privacy@mixsight.ai"
                    className="text-teal-600 hover:underline"
                  >
                    privacy@mixsight.ai
                  </a>
                </p>
                <p>
                  <span className="font-medium">Security issues:</span>{" "}
                  <a
                    href="mailto:security@mixsight.ai"
                    className="text-teal-600 hover:underline"
                  >
                    security@mixsight.ai
                  </a>
                </p>
                <p>
                  <span className="font-medium">General:</span>{" "}
                  <a
                    href="mailto:hello@mixsight.ai"
                    className="text-teal-600 hover:underline"
                  >
                    hello@mixsight.ai
                  </a>
                </p>
              </div>
            </section>
          </div>
        </article>
      </main>
      <Footer />
    </>
  );
}
