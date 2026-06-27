import { currentUser } from "@clerk/nextjs/server";
import { SignOutButton } from "@clerk/nextjs";

export default async function HomePage() {
  const user = await currentUser();
  const email = user?.emailAddresses[0]?.emailAddress ?? "unknown";

  return (
    <main className="min-h-screen flex items-center justify-center bg-[#0f1e3d] text-white px-4">
      <div className="max-w-md text-center">
        <h1 className="text-3xl font-semibold mb-3">MixSight</h1>
        <p className="text-white/60 mb-6">Signed in as {email}.</p>
        <p className="text-xs text-white/40 mb-8">
          Phase 1a Week 1 skeleton. Pacing surfaces land Week 3 (§7.3).
        </p>
        <SignOutButton>
          <button
            type="button"
            className="text-sm text-teal-300 hover:text-teal-200 underline-offset-4 hover:underline"
          >
            Sign out
          </button>
        </SignOutButton>
      </div>
    </main>
  );
}
