"use client";

import * as Clerk from "@clerk/elements/common";
import * as SignUp from "@clerk/elements/sign-up";
import Image from "next/image";

const cardClass =
  "bg-white/[0.04] border border-white/10 rounded-2xl p-6 backdrop-blur";
const labelClass = "block text-xs uppercase tracking-wider text-white/50 mb-2";
const inputClass =
  "w-full bg-white/5 border border-white/15 rounded-lg px-3.5 py-2.5 text-sm focus:outline-none focus:border-teal-400/80 focus:ring-2 focus:ring-teal-400/20 placeholder:text-white/30";
const submitClass =
  "w-full inline-flex items-center justify-center gap-2 bg-teal-500 hover:bg-teal-400 text-[#0f1e3d] font-medium rounded-lg px-4 py-2.5 text-sm transition-colors disabled:bg-teal-500/50";
const errorClass = "mt-1 text-xs text-rose-300";

export default function SignUpPage() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-[#0f1e3d] text-white px-4 py-12">
      <div className="w-full max-w-md">
        <div className="flex flex-col items-center mb-8">
          <div className="bg-white rounded-2xl p-3 mb-6 shadow-2xl">
            <Image src="/logo.png" alt="MixSight" width={140} height={36} priority />
          </div>
          <h1 className="text-2xl font-semibold text-center leading-snug">
            Create your account.
          </h1>
        </div>

        <SignUp.Root>
          <SignUp.Step name="start" className={cardClass}>
            <Clerk.Field name="emailAddress" className="block mb-4">
              <Clerk.Label className={labelClass}>Email</Clerk.Label>
              <Clerk.Input type="email" required className={inputClass} />
              <Clerk.FieldError className={errorClass} />
            </Clerk.Field>
            <Clerk.Field name="password" className="block mb-4">
              <Clerk.Label className={labelClass}>Password</Clerk.Label>
              <Clerk.Input type="password" required className={inputClass} />
              <Clerk.FieldError className={errorClass} />
            </Clerk.Field>
            {/* Mount point for Clerk's Smart CAPTCHA. Without this div Clerk falls
                back to Invisible CAPTCHA (weaker bot protection) and warns in the
                console. Sign-in doesn't need an equivalent — sign-up is the
                bot-protected surface. */}
            <div id="clerk-captcha" className="mb-4 empty:mb-0" />
            <SignUp.Action submit className={submitClass}>
              Continue
            </SignUp.Action>
          </SignUp.Step>

          <SignUp.Step name="verifications" className={cardClass}>
            <SignUp.Strategy name="email_code">
              <Clerk.Field name="code" className="block mb-4">
                <Clerk.Label className={labelClass}>Email code</Clerk.Label>
                <Clerk.Input required className={inputClass} />
                <Clerk.FieldError className={errorClass} />
              </Clerk.Field>
              <SignUp.Action submit className={submitClass}>
                Verify
              </SignUp.Action>
            </SignUp.Strategy>
          </SignUp.Step>

          <Clerk.GlobalError className="mt-4 text-xs text-rose-300" />
        </SignUp.Root>

        {/* See sign-in page note — plain <a> avoids the Next/Clerk Link race. */}
        <p className="text-center text-sm text-white/50 mt-6">
          Already have an account?{" "}
          <a href="/sign-in" className="text-teal-300 hover:text-teal-200">
            Sign in
          </a>
        </p>
      </div>
    </main>
  );
}
