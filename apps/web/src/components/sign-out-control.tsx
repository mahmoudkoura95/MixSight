"use client";

import { SignOutButton } from "@clerk/nextjs";

/**
 * Styled sign-out control. Kept as a client component because
 * `<SignOutButton>` clones its single child via `React.Children.only`, which
 * fails when the child is passed across the RSC boundary from an async server
 * component (the error is "multiple children components to <SignOutButton/>").
 */
export function SignOutControl() {
  return (
    <SignOutButton>
      <button
        type="button"
        className="w-full rounded-lg border border-white/15 px-4 py-2.5 text-sm text-white/80 transition-colors hover:border-white/30 hover:bg-white/5"
      >
        Sign out
      </button>
    </SignOutButton>
  );
}
