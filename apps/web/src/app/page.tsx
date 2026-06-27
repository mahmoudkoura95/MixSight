import { currentUser } from "@clerk/nextjs/server";

import { SignOutControl } from "@/components/sign-out-control";

export default async function HomePage() {
  const user = await currentUser();
  const email = user?.emailAddresses[0]?.emailAddress ?? "unknown";
  // Local demo only: set NEXT_PUBLIC_DEMO_PACING_PATH to the path the seed
  // script prints. Until a real onboarding/client-list surface exists
  // (Phase 1b), this is how you reach the single pacing surface.
  const demoPacingPath = process.env.NEXT_PUBLIC_DEMO_PACING_PATH;

  return (
    <main className="min-h-screen flex items-center justify-center bg-[#0f1e3d] text-white px-4">
      <div className="max-w-md w-full space-y-6 text-center">
        <div>
          <h1 className="text-3xl font-semibold mb-2">MixSight</h1>
          <p className="text-sm text-white/60">Signed in as {email}.</p>
        </div>

        {demoPacingPath ? (
          <a
            href={demoPacingPath}
            className="block w-full rounded-lg bg-teal-500 px-4 py-2.5 font-medium text-[#0f1e3d] transition-colors hover:bg-teal-400"
          >
            View pacing snapshot →
          </a>
        ) : (
          <p className="text-xs text-white/40">
            No demo workspace linked. Run the seed script and set
            <code className="mx-1 text-white/60">NEXT_PUBLIC_DEMO_PACING_PATH</code>
            to surface the pacing view here.
          </p>
        )}

        <SignOutControl />
      </div>
    </main>
  );
}
