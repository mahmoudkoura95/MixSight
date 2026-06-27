# Modeling engine conventions

**Phase 2 territory.** In Phase 1 this directory holds only the interface skeleton and a stubbed engine; do not implement Bayesian model code in Phase 1.

## The contract

Every modeling engine implements a stable interface so engines are swappable. PyMC-Marketing ships in Phase 2a; Meridian is evaluated in Phase 2b/2c with a 2-day spike; the default may switch in Phase 2c without breaking the rest of the system.

```python
class ModelingEngine(Protocol):
    async def fit(
        self,
        client_id: UUID,
        training_window_start: date,
        training_window_end: date,
        config: FitConfig,
    ) -> ContributionFit: ...
    async def predict(
        self,
        fit: ContributionFit,
        scenario: Scenario,
    ) -> Trajectory: ...
    async def marginal_roas(
        self,
        fit: ContributionFit,
        channel: str,
        current_spend: Decimal,
    ) -> MarginalRoasCurve: ...
    async def diagnostics(self, fit: ContributionFit) -> Diagnostics: ...
```

## Model components (§8.2)

- Geometric adstock (per-channel decay).
- Hill function saturation (half-saturation point and shape per channel).
- Fourier seasonality.
- Per-market promotional event flags from `PromotionalEvent`.
- Macro controls: Google Trends, holidays, optional weather/CPI from `MacroSignal`.
- Hierarchical structure: per-channel coefficients pool across markets; market intercepts independent.
- Additional pooling layers across taxonomy dimensions (product_line, etc.) when data supports.

## Refit cadence

Weekly background job. 30-90 minutes per client. Asynchronous. Queue + dedicated worker by Phase 2c.

## What lives here

- `modeling/engines/base.py` — the Protocol, the dataclasses, exception types.
- `modeling/engines/pymc/` — PyMC-Marketing implementation (Phase 2a+).
- `modeling/engines/meridian/` — Meridian implementation (Phase 2b spike, Phase 2c decision).
- `modeling/engines/stub/` — a deterministic stub engine used in tests and Phase 1 development.
- `modeling/diagnostics/` — engine-agnostic diagnostics rendering (trace plots, posterior predictive checks, residuals).

## What does NOT live here

- API routes — those live in `apps/api/routes/modeling/`.
- Frontend rendering — that lives in `apps/web/`.
- Persistence — `ContributionFit`, `IncrementalityResult`, `ForecastRun` are SQLModel tables in `apps/api/models/`. Engines return data; the API layer persists.

## Phase 1 stance

- The Protocol, dataclasses, and stub engine ship in Phase 1a.
- `ContributionFit` table provisioned empty (per §7.21 — no schema retrofit).
- No PyMC, no Meridian imports anywhere in Phase 1 code.
- The reallocation engine in Phase 1 uses heuristic projection (§7.10 step 5). Phase 2d replaces that step with curve-based projection from the modeling engine — interface, not internals.

## Watch-outs (Phase 2 will surface these)

- **Identifiability.** Hierarchical pooling without enough variance per market produces unstable channel coefficients. Diagnostics must flag this.
- **Refit performance.** A 90-minute weekly fit per client is fine for 10 clients. 100 clients needs partial refits, caching, dedicated workers.
- **Calibration without incrementality.** A model that fits well in-sample but has no lift test to calibrate against is producing precision without accuracy. Make CI ranges honest.
- **Engine swap.** PyMC and Meridian disagree about parameterization. The interface must hide that.
- **Taxonomy pooling parameter explosion.** Adding a product_line pooling layer multiplies parameters. Only enable when sample size per (channel, market, product_line) supports.
