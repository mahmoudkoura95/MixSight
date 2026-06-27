import type { Metadata } from "next";
import { Nav } from "@/components/nav";
import { Footer } from "@/components/footer";

export const metadata: Metadata = {
  title: "Terms of Service",
  description:
    "MixSight terms of service — the agreement governing use of the platform.",
};

export default function TermsPage() {
  return (
    <>
      <Nav />
      <main id="main" className="py-16 px-4 sm:px-6 lg:px-8">
        <article className="max-w-3xl mx-auto">
          <header className="mb-10">
            <h1 className="text-3xl font-bold text-slate-900 mb-2">
              Terms of Service
            </h1>
            <p className="text-sm text-slate-500">Last updated: May 13, 2026</p>
          </header>

          <div className="space-y-8 text-sm text-slate-700 leading-relaxed">
            <section aria-labelledby="t1">
              <h2 id="t1" className="text-lg font-semibold text-slate-900 mb-3">
                1. Acceptance of terms
              </h2>
              <p>
                These Terms of Service (“Terms”) govern your access to and use
                of the MixSight platform available at{" "}
                <span className="font-medium">app.mixsight.ai</span> and the
                related services operated by MixSight (“we,” “us,” or “our”).
                By creating an account or using the Service, you agree to be
                bound by these Terms and our{" "}
                <a href="/privacy/" className="text-teal-600 hover:underline">
                  Privacy Policy
                </a>
                .
              </p>
              <p className="mt-3">
                If you are using the Service on behalf of an organization, you
                represent that you have authority to bind that organization to
                these Terms, and references to “you” include that organization.
              </p>
            </section>

            <section aria-labelledby="t2">
              <h2 id="t2" className="text-lg font-semibold text-slate-900 mb-3">
                2. Description of service
              </h2>
              <p>
                MixSight is a paid media pacing and measurement platform for
                performance marketing agencies. The Service includes:
              </p>
              <ul className="mt-2 space-y-1 list-disc pl-5">
                <li>
                  Connection to advertising platforms (Meta, Google Ads, GA4,
                  TikTok) via OAuth to retrieve campaign performance data.
                </li>
                <li>
                  Weekly pacing snapshot generation, drift detection, and
                  reallocation analysis.
                </li>
                <li>
                  AI-assisted features including plan parsing, drift
                  explanations, and defense-kit narrative generation via the
                  Anthropic API.
                </li>
                <li>
                  Defense-kit generation: branded HTML and PDF reports for
                  client presentations.
                </li>
                <li>
                  Multi-market, multi-currency campaign management tools.
                </li>
              </ul>
            </section>

            <section aria-labelledby="t3">
              <h2 id="t3" className="text-lg font-semibold text-slate-900 mb-3">
                3. Account registration
              </h2>
              <p>
                To use the Service, you must create an account via Clerk
                authentication. You agree to:
              </p>
              <ul className="mt-2 space-y-1 list-disc pl-5">
                <li>Provide accurate and complete registration information.</li>
                <li>
                  Keep your credentials secure and not share account access.
                </li>
                <li>
                  Promptly notify us of unauthorized account access at{" "}
                  <a
                    href="mailto:security@mixsight.ai"
                    className="text-teal-600 hover:underline"
                  >
                    security@mixsight.ai
                  </a>
                  .
                </li>
                <li>Be responsible for all activity under your account.</li>
              </ul>
              <p className="mt-3">
                We reserve the right to disable accounts that violate these
                Terms.
              </p>
            </section>

            <section aria-labelledby="t4">
              <h2 id="t4" className="text-lg font-semibold text-slate-900 mb-3">
                4. Subscription and billing
              </h2>

              <h3 className="font-medium text-slate-900 mb-2">
                4.1 Plans and pricing
              </h3>
              <p>
                The Service is offered on a subscription basis. Current plans
                and pricing are available at{" "}
                <a href="/pricing/" className="text-teal-600 hover:underline">
                  mixsight.ai/pricing
                </a>
                . We reserve the right to modify pricing with 30 days’ written
                notice to active subscribers.
              </p>

              <h3 className="font-medium text-slate-900 mt-4 mb-2">
                4.2 30-day pilot
              </h3>
              <p>
                New accounts begin with a 30-day pilot period. No credit card
                is required to start the pilot. At the end of the pilot, you
                must subscribe to a paid plan or your account will be
                deactivated. Data is retained for 30 days after deactivation
                before permanent deletion.
              </p>

              <h3 className="font-medium text-slate-900 mt-4 mb-2">
                4.3 Payment
              </h3>
              <p>
                Subscription fees are billed monthly or annually (15% prepay
                discount) via Stripe. Fees are non-refundable except as
                required by law or as described in these Terms. Overage charges
                for additional seats or workspaces are billed at the end of
                each billing cycle.
              </p>

              <h3 className="font-medium text-slate-900 mt-4 mb-2">
                4.4 BYOK LLM credit
              </h3>
              <p>
                When you configure a per-workspace Anthropic API key (BYOK), a
                credit of $200 per BYOK-active workspace is applied to your
                next invoice. The credit is non-transferable and applies only
                to the billing period during which BYOK was active.
              </p>

              <h3 className="font-medium text-slate-900 mt-4 mb-2">
                4.5 Annual prepay
              </h3>
              <p>
                Annual prepay is non-refundable except in the case of service
                termination by MixSight. In that event, we will refund the
                prorated unused portion of your prepay.
              </p>
            </section>

            <section aria-labelledby="t5">
              <h2 id="t5" className="text-lg font-semibold text-slate-900 mb-3">
                5. Acceptable use
              </h2>
              <p>You agree not to:</p>
              <ul className="mt-2 space-y-1 list-disc pl-5">
                <li>
                  Use the Service for any unlawful purpose or in violation of
                  any applicable advertising platform terms of service.
                </li>
                <li>
                  Access advertising accounts you are not authorized to access.
                </li>
                <li>
                  Attempt to reverse-engineer, decompile, or extract the source
                  code of the Service.
                </li>
                <li>
                  Use automated means to scrape or extract data from the
                  Service beyond your authorized use.
                </li>
                <li>
                  Share account credentials with individuals outside your
                  organization.
                </li>
                <li>
                  Resell or sublicense the Service without written permission.
                </li>
                <li>
                  Introduce malicious code or attempt to compromise the Service
                  or its infrastructure.
                </li>
              </ul>
            </section>

            <section aria-labelledby="t6">
              <h2 id="t6" className="text-lg font-semibold text-slate-900 mb-3">
                6. Your data and our license to use it
              </h2>
              <p>
                You retain ownership of all data you upload or generate within
                the Service, including media plans, advertising platform data
                retrieved via OAuth, and any content you create.
              </p>
              <p className="mt-3">
                You grant us a limited, non-exclusive license to store,
                process, and display your data solely as necessary to provide
                the Service. We do not claim any ownership rights over your
                data.
              </p>
              <p className="mt-3">
                We do not use your data to train AI models, share it with third
                parties for commercial purposes, or use it for any purpose
                other than providing the Service, as described in our{" "}
                <a href="/privacy/" className="text-teal-600 hover:underline">
                  Privacy Policy
                </a>
                .
              </p>
            </section>

            <section aria-labelledby="t7">
              <h2 id="t7" className="text-lg font-semibold text-slate-900 mb-3">
                7. Advertising platform API usage
              </h2>
              <p>
                Your use of platform connectors (Meta, Google Ads, GA4, TikTok)
                is subject to the terms of service of the respective
                advertising platforms in addition to these Terms. You are
                responsible for maintaining your authorization to access your
                clients’ advertising accounts. MixSight is not responsible for
                interruptions in data access resulting from changes to platform
                API policies or your authorization status.
              </p>
              <p className="mt-3">
                You represent that you are an authorized representative of the
                advertising accounts you connect to MixSight and that you have
                the right to grant MixSight access to that data on behalf of
                your clients.
              </p>
            </section>

            <section aria-labelledby="t8">
              <h2 id="t8" className="text-lg font-semibold text-slate-900 mb-3">
                8. AI-generated content
              </h2>
              <p>
                The Service uses AI models (via the Anthropic API) to generate
                content including drift explanations, plan parsing
                suggestions, and defense-kit narratives. You acknowledge that:
              </p>
              <ul className="mt-2 space-y-1 list-disc pl-5">
                <li>
                  AI-generated content may be inaccurate, incomplete, or
                  inappropriate for specific use cases. You are responsible for
                  reviewing and verifying AI-generated outputs before using
                  them in client-facing materials.
                </li>
                <li>
                  Reallocation suggestions are analytical outputs for your
                  consideration, not financial or investment advice. MixSight
                  does not recommend specific budget allocations.
                </li>
                <li>
                  We do not guarantee availability of AI features at any
                  specific time. Degraded-mode fallbacks (templated narratives,
                  placeholder text) are provided to ensure the Service remains
                  usable during AI service interruptions.
                </li>
              </ul>
            </section>

            <section aria-labelledby="t9">
              <h2 id="t9" className="text-lg font-semibold text-slate-900 mb-3">
                9. Intellectual property
              </h2>
              <p>
                The Service, including its design, functionality, and
                underlying code, is the proprietary property of MixSight and is
                protected by applicable intellectual property laws. Nothing in
                these Terms grants you any right to the MixSight name, logo, or
                brand.
              </p>
              <p className="mt-3">
                White-label features (available on Growth tier and above)
                allow you to apply your agency’s branding to client-facing
                outputs. Your agency brand and any content you create remain
                your intellectual property.
              </p>
            </section>

            <section aria-labelledby="t10">
              <h2 id="t10" className="text-lg font-semibold text-slate-900 mb-3">
                10. Confidentiality
              </h2>
              <p>
                Each party agrees to keep confidential the other’s non-public
                information shared in connection with the Service. MixSight
                treats all customer data as confidential. You agree to keep
                confidential any non-public details of MixSight’s technical
                implementation, pricing not publicly available, and roadmap
                information shared in the course of your relationship with us.
              </p>
            </section>

            <section aria-labelledby="t11">
              <h2 id="t11" className="text-lg font-semibold text-slate-900 mb-3">
                11. Disclaimer of warranties
              </h2>
              <p>
                THE SERVICE IS PROVIDED “AS IS” AND “AS AVAILABLE.” WE DISCLAIM
                ALL WARRANTIES, EXPRESS OR IMPLIED, INCLUDING WARRANTIES OF
                MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
                NON-INFRINGEMENT. WE DO NOT WARRANT THAT THE SERVICE WILL BE
                UNINTERRUPTED, ERROR-FREE, OR THAT ANY DEFECTS WILL BE
                CORRECTED.
              </p>
              <p className="mt-3">
                Advertising platform data is retrieved from third-party APIs.
                We do not warrant the accuracy, completeness, or timeliness of
                data retrieved from Meta, Google, GA4, or TikTok. Data
                discrepancies between platforms are an inherent feature of the
                paid media landscape, not a defect in the Service.
              </p>
            </section>

            <section aria-labelledby="t12">
              <h2 id="t12" className="text-lg font-semibold text-slate-900 mb-3">
                12. Limitation of liability
              </h2>
              <p>
                TO THE MAXIMUM EXTENT PERMITTED BY LAW, IN NO EVENT WILL
                MIXSIGHT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL,
                CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING LOSS OF PROFITS,
                DATA, OR BUSINESS, ARISING FROM YOUR USE OF THE SERVICE.
              </p>
              <p className="mt-3">
                OUR AGGREGATE LIABILITY TO YOU FOR ANY CLAIM ARISING FROM THESE
                TERMS OR YOUR USE OF THE SERVICE SHALL NOT EXCEED THE AMOUNTS
                PAID BY YOU TO MIXSIGHT IN THE TWELVE (12) MONTHS PRECEDING THE
                CLAIM.
              </p>
            </section>

            <section aria-labelledby="t13">
              <h2 id="t13" className="text-lg font-semibold text-slate-900 mb-3">
                13. Termination
              </h2>

              <h3 className="font-medium text-slate-900 mb-2">13.1 By you</h3>
              <p>
                You may cancel your subscription at any time from your account
                settings. Cancellation takes effect at the end of the current
                billing cycle (monthly) or immediately (annual, subject to
                proration policy). A 30-day data grace period follows
                cancellation.
              </p>

              <h3 className="font-medium text-slate-900 mt-4 mb-2">13.2 By us</h3>
              <p>
                We may suspend or terminate your account for violation of
                these Terms, non-payment, or if we reasonably believe you pose
                a security or legal risk. We will provide notice where
                practicable. In the event of termination for cause, no refund
                is owed.
              </p>

              <h3 className="font-medium text-slate-900 mt-4 mb-2">
                13.3 Effect of termination
              </h3>
              <p>
                Upon termination, your right to use the Service ceases. OAuth
                credentials are deleted immediately. Customer data is deleted
                30 days after termination per our data retention policy. You
                may download a data export during the grace period.
              </p>
            </section>

            <section aria-labelledby="t14">
              <h2 id="t14" className="text-lg font-semibold text-slate-900 mb-3">
                14. Governing law and disputes
              </h2>
              <p>
                These Terms are governed by the laws of the State of Delaware,
                United States, without regard to its conflict-of-law
                provisions. Any dispute arising from these Terms or your use of
                the Service will be resolved by binding arbitration under the
                rules of the American Arbitration Association, except that
                either party may seek injunctive or other equitable relief in
                any court of competent jurisdiction.
              </p>
            </section>

            <section aria-labelledby="t15">
              <h2 id="t15" className="text-lg font-semibold text-slate-900 mb-3">
                15. Changes to these terms
              </h2>
              <p>
                We may update these Terms from time to time. We will notify you
                of material changes by email at least 30 days before the
                changes take effect. Your continued use of the Service after
                the effective date constitutes acceptance of the revised Terms.
              </p>
            </section>

            <section aria-labelledby="t16">
              <h2 id="t16" className="text-lg font-semibold text-slate-900 mb-3">
                16. Contact
              </h2>
              <p>Questions about these Terms:</p>
              <div className="mt-3 space-y-1">
                <p>
                  <span className="font-medium">Email:</span>{" "}
                  <a
                    href="mailto:legal@mixsight.ai"
                    className="text-teal-600 hover:underline"
                  >
                    legal@mixsight.ai
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
