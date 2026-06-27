import type { Metadata } from "next";
import { Suspense } from "react";
import { Clock, Mail, ShieldAlert, Scale } from "lucide-react";
import { Nav } from "@/components/nav";
import { Footer } from "@/components/footer";
import { ContactForm } from "@/components/contact-form";

export const metadata: Metadata = {
  title: "Contact",
  description:
    "Get in touch with MixSight. Early access requests, design partner inquiries, pricing questions, or general questions — we respond within one business day.",
};

const directChannels = [
  {
    icon: Mail,
    label: "General questions, early access, sales",
    email: "hello@mixsight.ai",
  },
  {
    icon: ShieldAlert,
    label: "Privacy requests, GDPR, data export",
    email: "privacy@mixsight.ai",
  },
  {
    icon: ShieldAlert,
    label: "Security issues and vulnerability reports",
    email: "security@mixsight.ai",
  },
  {
    icon: Scale,
    label: "Terms of service, contracts, legal",
    email: "legal@mixsight.ai",
  },
];

function FormSkeleton() {
  return (
    <div className="space-y-5" aria-hidden="true">
      <div className="grid sm:grid-cols-2 gap-5">
        <div className="h-[68px] rounded-lg bg-slate-100 animate-pulse" />
        <div className="h-[68px] rounded-lg bg-slate-100 animate-pulse" />
      </div>
      <div className="h-[68px] rounded-lg bg-slate-100 animate-pulse" />
      <div className="h-[68px] rounded-lg bg-slate-100 animate-pulse" />
      <div className="h-[180px] rounded-lg bg-slate-100 animate-pulse" />
      <div className="h-[44px] w-40 rounded-lg bg-slate-100 animate-pulse ml-auto" />
    </div>
  );
}

export default function ContactPage() {
  return (
    <>
      <Nav />
      <main id="main">
        <section className="pt-16 pb-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-4xl sm:text-5xl font-bold text-slate-900 mb-4">
              Get in touch
            </h1>
            <p className="text-lg text-slate-600 max-w-xl mx-auto">
              Tell us about your agency, the platforms you run, and what you’re
              looking for. We respond within one business day.
            </p>
          </div>
        </section>

        <section className="pb-24 px-4 sm:px-6 lg:px-8">
          <div className="max-w-5xl mx-auto grid lg:grid-cols-[2fr_1fr] gap-10">
            <div className="bg-white rounded-2xl border border-slate-200 p-6 sm:p-8">
              <Suspense fallback={<FormSkeleton />}>
                <ContactForm />
              </Suspense>
            </div>

            <aside className="space-y-6" aria-label="Direct contact channels">
              <div className="bg-slate-50 rounded-2xl border border-slate-200 p-6">
                <div className="flex items-center gap-2 mb-3">
                  <Clock
                    className="w-4 h-4 text-teal-600"
                    aria-hidden="true"
                  />
                  <h2 className="text-sm font-semibold text-slate-900">
                    Response time
                  </h2>
                </div>
                <p className="text-sm text-slate-600 leading-relaxed">
                  One business day for most inquiries. Same day for design
                  partner conversations. Security reports acknowledged within
                  four hours.
                </p>
              </div>

              <div className="bg-slate-50 rounded-2xl border border-slate-200 p-6">
                <h2 className="text-sm font-semibold text-slate-900 mb-3">
                  Or email us directly
                </h2>
                <ul className="space-y-3">
                  {directChannels.map(({ icon: Icon, label, email }) => (
                    <li key={email} className="flex gap-3">
                      <Icon
                        className="w-4 h-4 text-slate-400 flex-shrink-0 mt-0.5"
                        aria-hidden="true"
                      />
                      <div>
                        <p className="text-xs text-slate-500 mb-0.5">{label}</p>
                        <a
                          href={`mailto:${email}`}
                          className="text-sm text-teal-700 hover:underline font-medium"
                        >
                          {email}
                        </a>
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            </aside>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}
