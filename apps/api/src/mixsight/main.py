"""FastAPI app entrypoint.

Configures logging, installs the request-context middleware, mounts the
routers (Clerk webhooks, CSV actuals, pacing), and runs the startup
invariants: registering the §7.4 AuditLog hooks and the §7.19 tenancy route
audit, both of which fail loud at import. Also exposes `/healthz`.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from sqlalchemy import text

from mixsight.audit import register_audit_hooks
from mixsight.config import get_settings
from mixsight.connectors.csv.routes import router as csv_actuals_router
from mixsight.db import engine
from mixsight.logging import configure_logging, get_logger
from mixsight.middleware import RequestContextMiddleware
from mixsight.models import (
    Actuals,
    AdAccountMapping,
    CampaignLabelRule,
    Client,
    ClientTaxonomy,
    ConnectorAuth,
    ContributionFit,
    DefenseKit,
    EncryptedSecret,
    IncrementalityResult,
    MacroSignal,
    Market,
    MarketConfig,
    Organization,
    PacingSnapshot,
    PacingSnapshotLine,
    Plan,
    PlanLine,
    PromotionalEvent,
    ReallocationSuggestion,
    ReconciliationFactor,
    User,
    UserClientAccess,
)
from mixsight.pacing.routes import router as pacing_router
from mixsight.tenancy import audit_routes
from mixsight.webhooks.clerk import router as clerk_webhook_router

# Side-effect imports above are kept ordered so the tenancy_routes audit
# at startup sees every registered route.

configure_logging()
log = get_logger("mixsight.main")
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    log.info("startup.begin", environment=settings.ENVIRONMENT)
    yield
    await engine.dispose()
    log.info("shutdown.complete")


app = FastAPI(
    title="MixSight API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(RequestContextMiddleware)
app.include_router(clerk_webhook_router)
app.include_router(csv_actuals_router)
app.include_router(pacing_router)


def _startup_invariants(app: FastAPI) -> None:
    """Synchronous startup invariants — both fail loud on import.

    Module-load (not lifespan) so any context that touches `app` sees the
    same guarantee: pytest with direct engine access, uvicorn ASGI boot,
    plain `import mixsight.main` for tooling. Both checks are idempotent.
    """
    # Per audit-log skill: ConnectorAuthEvent is excluded (own audit trail);
    # AuditLog itself is excluded by the hook's no-recursion guard.
    register_audit_hooks(
        [
            Organization,
            User,
            UserClientAccess,
            Client,
            Market,
            EncryptedSecret,
            MarketConfig,
            ConnectorAuth,
            AdAccountMapping,
            ClientTaxonomy,
            CampaignLabelRule,
            Plan,
            PlanLine,
            Actuals,
            PacingSnapshot,
            PacingSnapshotLine,
            ReconciliationFactor,
            ReallocationSuggestion,
            DefenseKit,
            PromotionalEvent,
            # Phase 2/4 mutable entities — auditable when populated.
            MacroSignal,
            ContributionFit,
            IncrementalityResult,
            # Excluded per audit-log skill (append-only): RecommendationLog,
            # ConnectorPull, ForecastRun, ConnectorAuthEvent, AuditLog itself.
        ]
    )
    audit_routes(app)
    log.info("startup.invariants_ok")


_startup_invariants(app)


@app.get("/healthz")
async def healthz() -> dict[str, Any]:
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        result.scalar_one()
    return {"status": "ok", "environment": settings.ENVIRONMENT}
