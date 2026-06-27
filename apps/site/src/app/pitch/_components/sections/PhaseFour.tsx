import { PhaseSection } from "../chrome/PhaseSection";
import { phaseFour } from "../../_lib/content";
import { CalibrationDashboard } from "../mockups/CalibrationDashboard";
import { BenchmarkCards } from "../mockups/BenchmarkCards";
import { EnterpriseWhiteLabel } from "../mockups/EnterpriseWhiteLabel";

const registry = {
  CalibrationDashboard,
  BenchmarkCards,
  EnterpriseWhiteLabel,
};

export function PhaseFour() {
  return (
    <PhaseSection
      id="phase-4"
      // Months 23–33
      arcStart={23 / 33}
      arcEnd={33 / 33}
      data={phaseFour}
      registry={registry}
      accent="rose"
    />
  );
}
