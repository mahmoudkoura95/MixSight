"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useId, useRef, useState } from "react";
import { Loader2, CheckCircle2, AlertTriangle, Send } from "lucide-react";

type InquiryType =
  | "Early access request"
  | "Design partner inquiry"
  | "Pricing question"
  | "Enterprise inquiry"
  | "General question";

const INQUIRY_TYPES: InquiryType[] = [
  "Early access request",
  "Design partner inquiry",
  "Pricing question",
  "Enterprise inquiry",
  "General question",
];

const TOPIC_MAP: Record<string, InquiryType> = {
  "early-access": "Early access request",
  "design-partner": "Design partner inquiry",
  "pricing-starter": "Pricing question",
  "pricing-growth": "Pricing question",
  "pricing-agency": "Pricing question",
  enterprise: "Enterprise inquiry",
  general: "General question",
};

type Status =
  | { kind: "idle" }
  | { kind: "submitting" }
  | { kind: "success" }
  | { kind: "mailto-opened" }
  | { kind: "error"; message: string };

const WEB3FORMS_ENDPOINT = "https://api.web3forms.com/submit";
const ACCESS_KEY = process.env.NEXT_PUBLIC_WEB3FORMS_KEY ?? "";

function buildMailtoFallback(data: {
  name: string;
  email: string;
  company: string;
  inquiry: InquiryType;
  message: string;
}) {
  const subject = `[${data.inquiry}] from ${data.name || data.email}`;
  const lines = [
    `Name: ${data.name}`,
    `Email: ${data.email}`,
    data.company ? `Company: ${data.company}` : null,
    `Inquiry: ${data.inquiry}`,
    "",
    "Message:",
    data.message,
  ].filter(Boolean);
  const body = lines.join("\r\n");
  return `mailto:hello@mixsight.ai?subject=${encodeURIComponent(
    subject
  )}&body=${encodeURIComponent(body)}`;
}

export function ContactForm() {
  const searchParams = useSearchParams();
  const topicParam = searchParams.get("topic")?.toLowerCase() ?? "";
  const initialInquiry: InquiryType =
    TOPIC_MAP[topicParam] ?? "General question";

  const nameId = useId();
  const emailId = useId();
  const companyId = useId();
  const inquiryId = useId();
  const messageId = useId();
  const statusId = useId();

  const formRef = useRef<HTMLFormElement>(null);
  const successHeadingRef = useRef<HTMLHeadingElement>(null);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [company, setCompany] = useState("");
  // Inquiry is derived from the URL topic until the user overrides it. This avoids a
  // useEffect-driven state sync (flagged by react-hooks/set-state-in-effect in React 19)
  // while still letting CTA-driven topic changes update the selected option.
  const [inquiryOverride, setInquiryOverride] = useState<InquiryType | null>(
    null
  );
  const inquiry: InquiryType = inquiryOverride ?? initialInquiry;
  const [message, setMessage] = useState("");
  const [botcheck, setBotcheck] = useState("");
  const [status, setStatus] = useState<Status>({ kind: "idle" });

  // Move keyboard focus to the success heading after a terminal status transition.
  useEffect(() => {
    if (
      (status.kind === "success" || status.kind === "mailto-opened") &&
      successHeadingRef.current
    ) {
      successHeadingRef.current.focus();
    }
  }, [status]);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();

    if (botcheck) {
      // Honeypot tripped — silently succeed.
      setStatus({ kind: "success" });
      return;
    }

    const data = { name, email, company, inquiry, message };

    // Fallback: no Web3Forms key configured → open user's email client.
    // Distinct status so we don't misleadingly say "Message sent" — the user still
    // has to click Send in their email client.
    if (!ACCESS_KEY) {
      window.location.href = buildMailtoFallback(data);
      setStatus({ kind: "mailto-opened" });
      return;
    }

    setStatus({ kind: "submitting" });

    try {
      const response = await fetch(WEB3FORMS_ENDPOINT, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          access_key: ACCESS_KEY,
          from_name: "MixSight Contact Form",
          subject: `[${inquiry}] from ${name || email}`,
          name,
          email,
          company,
          inquiry,
          message,
          botcheck,
        }),
      });

      const json = (await response.json().catch(() => ({}))) as {
        success?: boolean;
        message?: string;
      };

      if (response.ok && json.success) {
        setStatus({ kind: "success" });
        formRef.current?.reset();
        setName("");
        setEmail("");
        setCompany("");
        setMessage("");
        setInquiryOverride(null);
      } else {
        setStatus({
          kind: "error",
          message:
            json.message ||
            "We couldn't send your message. Please try again or email hello@mixsight.ai directly.",
        });
      }
    } catch {
      setStatus({
        kind: "error",
        message:
          "We couldn't reach the server. Check your connection and try again, or email hello@mixsight.ai.",
      });
    }
  }

  if (status.kind === "success" || status.kind === "mailto-opened") {
    const isMailto = status.kind === "mailto-opened";
    return (
      <div
        className="rounded-2xl border border-teal-200 bg-teal-50 p-8 text-center"
        role="status"
        aria-live="polite"
        id={statusId}
      >
        <CheckCircle2
          className="w-10 h-10 text-teal-600 mx-auto mb-4"
          aria-hidden="true"
        />
        <h2
          ref={successHeadingRef}
          tabIndex={-1}
          className="text-xl font-semibold text-slate-900 mb-2 focus:outline-none"
        >
          {isMailto ? "Email client opened" : "Message sent — thank you"}
        </h2>
        <p className="text-sm text-slate-600 mb-6">
          {isMailto ? (
            <>
              Finish sending the draft in your email app to reach us. If your
              email client didn&apos;t open, send a message directly to{" "}
              <a
                href="mailto:hello@mixsight.ai"
                className="text-teal-700 hover:underline font-medium"
              >
                hello@mixsight.ai
              </a>
              .
            </>
          ) : (
            <>
              We respond within one business day. If your question is urgent,
              email{" "}
              <a
                href="mailto:hello@mixsight.ai"
                className="text-teal-700 hover:underline font-medium"
              >
                hello@mixsight.ai
              </a>{" "}
              directly.
            </>
          )}
        </p>
        <button
          type="button"
          onClick={() => setStatus({ kind: "idle" })}
          className="inline-flex items-center px-4 py-2 bg-white border border-slate-300 hover:border-slate-400 text-slate-700 font-medium rounded-lg transition-colors text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 focus-visible:ring-offset-2"
        >
          Send another message
        </button>
      </div>
    );
  }

  const isSubmitting = status.kind === "submitting";

  return (
    <form
      ref={formRef}
      onSubmit={handleSubmit}
      className="space-y-5"
      aria-describedby={status.kind === "error" ? statusId : undefined}
    >
      {/* Honeypot — hidden from real users, bots may fill it in. */}
      <div
        aria-hidden="true"
        style={{ position: "absolute", left: "-10000px", top: "auto" }}
      >
        <label htmlFor="botcheck-honeypot">Don&apos;t fill this out</label>
        <input
          type="text"
          id="botcheck-honeypot"
          name="botcheck"
          tabIndex={-1}
          autoComplete="off"
          value={botcheck}
          onChange={(e) => setBotcheck(e.target.value)}
        />
      </div>

      <div className="grid sm:grid-cols-2 gap-5">
        <div>
          <label
            htmlFor={nameId}
            className="block text-sm font-medium text-slate-900 mb-1.5"
          >
            Name <span className="text-red-600">*</span>
          </label>
          <input
            id={nameId}
            type="text"
            required
            autoComplete="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            disabled={isSubmitting}
            className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-500/30 disabled:bg-slate-50 disabled:cursor-not-allowed"
          />
        </div>
        <div>
          <label
            htmlFor={emailId}
            className="block text-sm font-medium text-slate-900 mb-1.5"
          >
            Email <span className="text-red-600">*</span>
          </label>
          <input
            id={emailId}
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={isSubmitting}
            className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-500/30 disabled:bg-slate-50 disabled:cursor-not-allowed"
          />
        </div>
      </div>

      <div>
        <label
          htmlFor={companyId}
          className="block text-sm font-medium text-slate-900 mb-1.5"
        >
          Company or agency
        </label>
        <input
          id={companyId}
          type="text"
          autoComplete="organization"
          value={company}
          onChange={(e) => setCompany(e.target.value)}
          disabled={isSubmitting}
          className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-500/30 disabled:bg-slate-50 disabled:cursor-not-allowed"
        />
      </div>

      <div>
        <label
          htmlFor={inquiryId}
          className="block text-sm font-medium text-slate-900 mb-1.5"
        >
          Inquiry type <span className="text-red-600">*</span>
        </label>
        <select
          id={inquiryId}
          required
          value={inquiry}
          onChange={(e) => setInquiryOverride(e.target.value as InquiryType)}
          disabled={isSubmitting}
          className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 bg-white focus:outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-500/30 disabled:bg-slate-50 disabled:cursor-not-allowed"
        >
          {INQUIRY_TYPES.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label
          htmlFor={messageId}
          className="block text-sm font-medium text-slate-900 mb-1.5"
        >
          Message <span className="text-red-600">*</span>
        </label>
        <textarea
          id={messageId}
          required
          rows={6}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          disabled={isSubmitting}
          placeholder="Tell us a bit about your agency, the platforms you run, and what you're looking for."
          className="w-full rounded-lg border border-slate-300 px-3.5 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:border-teal-500 focus:ring-2 focus:ring-teal-500/30 disabled:bg-slate-50 disabled:cursor-not-allowed resize-y"
        />
      </div>

      {status.kind === "error" && (
        <div
          id={statusId}
          role="alert"
          aria-live="assertive"
          className="rounded-lg border border-red-200 bg-red-50 p-4 flex gap-3"
        >
          <AlertTriangle
            className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5"
            aria-hidden="true"
          />
          <p className="text-sm text-red-800">{status.message}</p>
        </div>
      )}

      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pt-2">
        <p className="text-xs text-slate-500">
          By submitting, you agree to our{" "}
          <a href="/privacy/" className="text-teal-700 hover:underline">
            privacy policy
          </a>
          .
        </p>
        <button
          type="submit"
          disabled={isSubmitting}
          className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-teal-600 hover:bg-teal-700 disabled:bg-teal-400 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 focus-visible:ring-offset-2 min-w-[10rem]"
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
              Sending…
            </>
          ) : (
            <>
              Send message
              <Send className="w-4 h-4" aria-hidden="true" />
            </>
          )}
        </button>
      </div>
    </form>
  );
}
