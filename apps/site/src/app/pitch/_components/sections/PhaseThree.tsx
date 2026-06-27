import { PhaseSection } from "../chrome/PhaseSection";
import { phaseThree } from "../../_lib/content";
import { ForecastChart } from "../mockups/ForecastChart";
import { ReforecastDiff } from "../mockups/ReforecastDiff";
import { GeoHoldoutDesigner } from "../mockups/GeoHoldoutDesigner";

const registry = {
  ForecastChart,
  ReforecastDiff,
  GeoHoldoutDesigner,
};

export function PhaseThree() {
  return (
    <PhaseSection
      id="phase-3"
      // Months 15–23
      arcStart={15 / 33}
      arcEnd={23 / 33}
      data={phaseThree}
      registry={registry}
      accent="amber"
    />
  );
}
