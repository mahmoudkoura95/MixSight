import { auth, currentUser } from "@clerk/nextjs/server";
import { SignOutButton } from "@clerk/nextjs";
import Link from "next/link";

// Mirror of /sign-in layout — see that file for the trap-loop rationale.
export default async function SignUpLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { userId } = await auth();
  if (!userId) {
    return <>{children}</>;
  }
  const user = await currentUser();
  const email = user?.emailAddresses[0]?.emailAddress ?? "your account";
  return (
    <main className="min-h-screen flex items-center justify-center bg-[#0f1e3d] text-white px-4">
      <div className="max-w-md text-center">
        <h1 className="text-2xl font-semibold mb-3">You&apos;re already signed in</h1>
        <p className="text-white/60 mb-8">as {email}.</p>
        <div className="flex flex-col gap-3 items-center">
          <Link
            href="/"
            className="text-sm bg-teal-500 hover:bg-teal-400 text-[#0f1e3d] font-medium rounded-lg px-4 py-2.5 inline-flex items-center"
          >
            Continue to MixSight
          </Link>
          <SignOutButton>
            <button
              type="button"
              className="text-sm text-teal-300 hover:text-teal-200 underline-offset-4 hover:underline"
            >
              Sign out
            </button>
          </SignOutButton>
        </div>
      </div>
    </main>
  );
}
