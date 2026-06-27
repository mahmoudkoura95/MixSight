"use client";

import dynamic from "next/dynamic";

// Lazy-load the entire pitch content with ssr: false so the section text never
// appears in the prerendered HTML. The gate is the only thing in the static page;
// content lives in a separate chunk that loads after authentication.
const PitchContent = dynamic(
  () => import("./_components/PitchContent").then((m) => ({ default: m.PitchContent })),
  { ssr: false },
);

export default function PitchPage() {
  return <PitchContent />;
}
