import Link from "next/link";
import Image from "next/image";

export function Nav() {
  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur border-b border-slate-200">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link
            href="/"
            className="flex items-center gap-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 rounded-md"
            aria-label="MixSight home"
          >
            <Image
              src="/logo.png"
              alt=""
              width={140}
              height={36}
              priority
              className="h-8 w-auto"
            />
          </Link>

          <nav className="hidden md:flex items-center gap-8" aria-label="Primary">
            <Link
              href="/#features"
              className="text-sm text-slate-600 hover:text-slate-900 transition-colors"
            >
              Features
            </Link>
            <Link
              href="/pricing/"
              className="text-sm text-slate-600 hover:text-slate-900 transition-colors"
            >
              Pricing
            </Link>
            <Link
              href="/contact/"
              className="text-sm text-slate-600 hover:text-slate-900 transition-colors"
            >
              Contact
            </Link>
          </nav>

          <div className="flex items-center gap-3">
            <a
              href="https://app.mixsight.ai"
              className="hidden md:inline-flex text-sm text-slate-600 hover:text-slate-900 transition-colors"
            >
              Sign in
            </a>
            <Link
              href="/contact/?topic=early-access"
              className="inline-flex items-center px-4 py-2 bg-teal-600 hover:bg-teal-700 text-white text-sm font-medium rounded-lg transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-500 focus-visible:ring-offset-2"
            >
              Request access
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
