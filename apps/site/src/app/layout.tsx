import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "MixSight — Pacing & measurement for performance agencies",
    template: "%s | MixSight",
  },
  description:
    "MixSight turns Monday morning media review into a thirty-minute workflow. Weekly pacing, cross-platform evidence, and a branded defense-kit for performance agencies running multi-market campaigns.",
  metadataBase: new URL("https://mixsight.ai"),
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://mixsight.ai",
    siteName: "MixSight",
    title: "MixSight — Pacing & measurement for performance agencies",
    description:
      "Weekly pacing, cross-platform evidence, and a branded defense-kit for performance agencies running multi-market campaigns.",
  },
  twitter: {
    card: "summary_large_image",
    title: "MixSight",
    description:
      "Weekly pacing, cross-platform evidence, and a branded defense-kit for performance agencies.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full`}>
      <body className="min-h-full flex flex-col">
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-[100] focus:px-4 focus:py-2 focus:bg-teal-600 focus:text-white focus:rounded-md"
        >
          Skip to main content
        </a>
        {children}
      </body>
    </html>
  );
}
