"use client";

import * as Clerk from "@clerk/elements/common";
import * as SignIn from "@clerk/elements/sign-in";
import Image from "next/image";

const cardClass =
  "bg-white/[0.04] border border-white/10 rounded-2xl p-6 backdrop-blur";
const labelClass = "block text-xs uppercase tracking-wider text-white/50 mb-2";
const inputClass =
  "w-full bg-white/5 border border-white/15 rounded-lg px-3.5 py-2.5 text-sm focus:outline-none focus:border-teal-400/80 focus:ring-2 focus:ring-teal-400/20 placeholder:text-white/30";
const submitClass =
  "w-full inline-flex items-center justify-center gap-2 bg-teal-500 hover:bg-teal-400 text-[#0f1e3d] font-medium rounded-lg px-4 py-2.5 text-sm transition-colors disabled:bg-teal-500/50";
const errorClass = "mt-1 text-xs text-rose-300";

export default function SignInPage() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-[#0f1e3d] text-white px-4 py-12">
      <div className="w-full max-w-md">
        <div className="flex flex-col items-center mb-8">
          <div className="bg-white rounded-2xl p-3 mb-6 shadow-2xl">
            <Image src="/logo.png" alt="MixSight" width={140} height={36} priority />
          </div>
          <h1 className="text-2xl font-semibold text-center leading-snug">
            Welcome back.
          </h1>
        </div>

        <SignIn.Root>
          <SignIn.Step name="start" className={cardClass}>
            <Clerk.Field name="identifier" className="block mb-4">
              <Clerk.Label className={labelClass}>Email</Clerk.Label>
              <Clerk.Input type="email" required className={inputClass} />
              <Clerk.FieldError className={errorClass} />
            </Clerk.Field>
            <SignIn.Action submit className={submitClass}>
              Continue
            </SignIn.Action>
          </SignIn.Step>

          <SignIn.Step name="verifications" className={cardClass}>
            <SignIn.Strategy name="password">
              <Clerk.Field name="password" className="block mb-4">
                <Clerk.Label className={labelClass}>Password</Clerk.Label>
                <Clerk.Input type="password" required className={inputClass} />
                <Clerk.FieldError className={errorClass} />
              </Clerk.Field>
              <SignIn.Action submit className={submitClass}>
                Sign in
              </SignIn.Action>
            </SignIn.Strategy>

            <SignIn.Strategy name="email_code">
              <Clerk.Field name="code" className="block mb-4 mt-4">
                <Clerk.Label className={labelClass}>Email code</Clerk.Label>
                <Clerk.Input required className={inputClass} />
                <Clerk.FieldError className={errorClass} />
              </Clerk.Field>
              <SignIn.Action submit className={submitClass}>
                Verify
              </SignIn.Action>
            </SignIn.Strategy>
          </SignIn.Step>

          <Clerk.GlobalError className="mt-4 text-xs text-rose-300" />
        </SignIn.Root>

        {/* Plain <a>, not next/link: under Next 16 + Clerk Elements the Link
            click can be swallowed before the router is ready, leaving the
            user on /sign-in with nothing visibly happening. A full reload on
            an auth page is fine and always fires. */}
        <p className="text-center text-sm text-white/50 mt-6">
          New here?{" "}
          <a href="/sign-up" className="text-teal-300 hover:text-teal-200">
            Create an account
          </a>
        </p>
      </div>
    </main>
  );
}
