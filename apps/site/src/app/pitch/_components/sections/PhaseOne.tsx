import { PhaseSection } from "../chrome/PhaseSection";
import { phaseOne } from "../../_lib/content";
import { PacingTableMock } from "../mockups/PacingTableMock";
import { EvidenceColumnExpanded } from "../mockups/EvidenceColumnExpanded";
import { DefenseKitAssembly } from "../mockups/DefenseKitAssembly";
import { ReallocationCards } from "../mockups/ReallocationCards";
import { ConnectorHealthGrid } from "../mockups/ConnectorHealthGrid";
import { EmptyStateGallery } from "../mockups/EmptyStateGallery";
import { FreshnessUXSplit } from "../mockups/FreshnessUXSplit";

const registry = {
  PacingTableMock,
  EvidenceColumnExpanded,
  DefenseKitAssembly,
  ReallocationCards,
  ConnectorHealthGrid,
  EmptyStateGallery,
  FreshnessUXSplit,
};

export function PhaseOne() {
  return (
    <PhaseSection
      id="phase-1"
      // Months 1–7 of a ~33-month arc.
      arcStart={0}
      arcEnd={7 / 33}
      data={phaseOne}
      registry={registry}
      accent="teal"
    />
  );
}
