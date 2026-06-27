import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "MixSight",
  description: "The Monday morning workflow for media agencies.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider>
      <html lang="en" className={inter.variable}>
        {/* Browser extensions (password managers, clippers) inject classes/attrs
            on <body> before React hydrates. Under React 19 + Next 16 that can
            leave subtrees un-hydrated, so buttons render but never wire up. */}
        <body suppressHydrationWarning>{children}</body>
      </html>
    </ClerkProvider>
  );
}
