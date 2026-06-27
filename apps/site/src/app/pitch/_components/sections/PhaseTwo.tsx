import { PhaseSection } from "../chrome/PhaseSection";
import { phaseTwo } from "../../_lib/content";
import { EvidenceColumnFour } from "../mockups/EvidenceColumnFour";
import { MarginalROASCurve } from "../mockups/MarginalROASCurve";
import { MMMDiagnosticsPanel } from "../mockups/MMMDiagnosticsPanel";
import { PromotionalCalendar } from "../mockups/PromotionalCalendar";

const registry = {
  EvidenceColumnFour,
  MarginalROASCurve,
  MMMDiagnosticsPanel,
  PromotionalCalendar,
};

export function PhaseTwo() {
  return (
    <PhaseSection
      id="phase-2"
      // Months 8–15
      arcStart={7 / 33}
      arcEnd={15 / 33}
      data={phaseTwo}
      registry={registry}
      accent="indigo"
    />
  );
}
