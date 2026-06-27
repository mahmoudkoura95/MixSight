"use client";

/* eslint-disable react-hooks/set-state-in-effect -- gate reads sessionStorage on mount, intentional hydration sync */

import { useEffect, useState, useTransition } from "react";
import Image from "next/image";
import { Lock, ArrowRight } from "lucide-react";
import { hashCredentials, getExpectedHash, SESSION_KEY } from "../_lib/gate";

type Props = {
  children: React.ReactNode;
};

export function PasswordGate({ children }: Props) {
  const [authed, setAuthed] = useState(false);
  const [hydrated, setHydrated] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  useEffect(() => {
    setHydrated(true);
    if (typeof window !== "undefined" && window.sessionStorage.getItem(SESSION_KEY) === "1") {
      setAuthed(true);
    }
  }, []);

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    const expected = getExpectedHash();
    if (!expected) {
      setError("Gate not configured. Set NEXT_PUBLIC_PITCH_PASSWORD_HASH in .env.local.");
      return;
    }
    const candidate = await hashCredentials(username, password);
    // Constant-ish-time pause to slow brute force.
    await new Promise((r) => setTimeout(r, 700));
    if (candidate === expected) {
      window.sessionStorage.setItem(SESSION_KEY, "1");
      startTransition(() => setAuthed(true));
    } else {
      setError("Those credentials don't match. Try again.");
    }
  }

  if (!hydrated) {
    // Avoid SSR/CSR mismatch on first paint.
    return <GateShell />;
  }

  if (authed) {
    return <>{children}</>;
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-[#0f1e3d] text-white px-4 py-12">
      <div className="w-full max-w-md">
        <div className="flex flex-col items-center mb-8">
          <div className="bg-white rounded-2xl p-3 mb-6 shadow-2xl">
            <Image src="/logo.png" alt="MixSight" width={140} height={36} priority />
          </div>
          <p className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-teal-300/90 mb-3">
            <Lock className="w-3 h-3" aria-hidden />
            Private preview
          </p>
          <h1 className="text-2xl font-semibold text-center leading-snug">
            For design partner consideration only.
          </h1>
          <p className="text-sm text-white/60 text-center mt-3 leading-relaxed">
            This page contains the full Phase 1–4 product vision, including unshipped
            features. Please don&apos;t share the URL or its contents.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="bg-white/[0.04] border border-white/10 rounded-2xl p-6 backdrop-blur">
          <label className="block text-xs uppercase tracking-wider text-white/50 mb-2" htmlFor="pitch-username">
            Username
          </label>
          <input
            id="pitch-username"
            type="text"
            autoComplete="username"
            required
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full bg-white/5 border border-white/15 rounded-lg px-3.5 py-2.5 text-sm mb-4 focus:outline-none focus:border-teal-400/80 focus:ring-2 focus:ring-teal-400/20 placeholder:text-white/30"
            placeholder=""
          />

          <label className="block text-xs uppercase tracking-wider text-white/50 mb-2" htmlFor="pitch-password">
            Password
          </label>
          <input
            id="pitch-password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full bg-white/5 border border-white/15 rounded-lg px-3.5 py-2.5 text-sm mb-5 focus:outline-none focus:border-teal-400/80 focus:ring-2 focus:ring-teal-400/20 placeholder:text-white/30"
            placeholder=""
          />

          <button
            type="submit"
            disabled={isPending}
            className="w-full inline-flex items-center justify-center gap-2 bg-teal-500 hover:bg-teal-400 disabled:bg-teal-500/50 text-[#0f1e3d] font-medium rounded-lg px-4 py-2.5 text-sm transition-colors"
          >
            {isPending ? "Unlocking…" : "Enter"}
            {!isPending && <ArrowRight className="w-4 h-4" aria-hidden />}
          </button>

          {error && (
            <p className="mt-4 text-xs text-rose-300 leading-relaxed" role="alert">
              {error}
            </p>
          )}
        </form>

        <p className="text-center text-xs text-white/40 mt-6">
          MixSight · mixsight.ai · Confidential
        </p>
      </div>
    </main>
  );
}

function GateShell() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-[#0f1e3d]">
      <div className="text-white/30 text-xs uppercase tracking-widest">Loading…</div>
    </main>
  );
}
