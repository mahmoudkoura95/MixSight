import Link from "next/link";
import Image from "next/image";

export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="mt-auto border-t border-slate-200 bg-slate-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col md:flex-row items-start md:items-start justify-between gap-10">
          <div className="max-w-xs">
            <Image
              src="/logo.png"
              alt="MixSight"
              width={120}
              height={32}
              className="h-7 w-auto mb-3"
            />
            <p className="text-sm text-slate-500 leading-relaxed">
              Pacing and measurement for performance marketing agencies.
            </p>
          </div>

          <nav
            aria-label="Footer"
            className="grid grid-cols-2 sm:grid-cols-3 gap-8"
          >
            <div className="flex flex-col gap-2">
              <span className="text-xs font-semibold text-slate-900 uppercase tracking-wide mb-1">
                Product
              </span>
              <Link
                href="/#features"
                className="text-sm text-slate-500 hover:text-slate-900 transition-colors"
              >
                Features
              </Link>
              <Link
                href="/pricing/"
                className="text-sm text-slate-500 hover:text-slate-900 transition-colors"
              >
                Pricing
              </Link>
            </div>
            <div className="flex flex-col gap-2">
              <span className="text-xs font-semibold text-slate-900 uppercase tracking-wide mb-1">
                Company
              </span>
              <Link
                href="/contact/"
                className="text-sm text-slate-500 hover:text-slate-900 transition-colors"
              >
                Contact
              </Link>
              <a
                href="https://app.mixsight.ai"
                className="text-sm text-slate-500 hover:text-slate-900 transition-colors"
              >
                Sign in
              </a>
            </div>
            <div className="flex flex-col gap-2">
              <span className="text-xs font-semibold text-slate-900 uppercase tracking-wide mb-1">
                Legal
              </span>
              <Link
                href="/privacy/"
                className="text-sm text-slate-500 hover:text-slate-900 transition-colors"
              >
                Privacy policy
              </Link>
              <Link
                href="/terms/"
                className="text-sm text-slate-500 hover:text-slate-900 transition-colors"
              >
                Terms of service
              </Link>
            </div>
          </nav>
        </div>

        <div className="mt-10 pt-6 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-3">
          <p className="text-xs text-slate-400">
            &copy; {year} MixSight. All rights reserved.
          </p>
          <p className="text-xs text-slate-400">
            Built for performance agencies · mixsight.ai
          </p>
        </div>
      </div>
    </footer>
  );
}
