import type { Metadata } from "next";
import { PasswordGate } from "./_components/PasswordGate";

export const metadata: Metadata = {
  title: { absolute: "MixSight — Private preview" },
  description: "Private pitch preview. Not for redistribution.",
  robots: {
    index: false,
    follow: false,
    nocache: true,
    googleBot: { index: false, follow: false, noimageindex: true },
  },
};

export default function PitchLayout({ children }: { children: React.ReactNode }) {
  return <PasswordGate>{children}</PasswordGate>;
}
