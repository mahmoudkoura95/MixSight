"use client";

import { PitchNav } from "./chrome/PitchNav";
import { Hero } from "./sections/Hero";
import { MondayMorningProblem } from "./sections/MondayMorningProblem";
import { WhatsDifferent } from "./sections/WhatsDifferent";
import { PhaseOne } from "./sections/PhaseOne";
import { PhaseTwo } from "./sections/PhaseTwo";
import { PhaseThree } from "./sections/PhaseThree";
import { PhaseFour } from "./sections/PhaseFour";
import { Beyond } from "./sections/Beyond";
import { Pricing } from "./sections/Pricing";
import { DesignPartnerAsk } from "./sections/DesignPartnerAsk";
import { FounderContact } from "./sections/FounderContact";
import { PitchFooter } from "./sections/PitchFooter";

export function PitchContent() {
  return (
    <div className="bg-[#0f1e3d] text-white selection:bg-teal-400 selection:text-[#0f1e3d]">
      <PitchNav />
      <Hero />
      <MondayMorningProblem />
      <WhatsDifferent />
      <PhaseOne />
      <PhaseTwo />
      <PhaseThree />
      <PhaseFour />
      <Beyond />
      <Pricing />
      <DesignPartnerAsk />
      <FounderContact />
      <PitchFooter />
    </div>
  );
}
