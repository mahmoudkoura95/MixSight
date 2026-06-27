"""GET endpoints for pacing snapshots + reallocation suggestions.

Both endpoints generate-on-demand: if a snapshot or suggestion set doesn't
exist for the resolved week, compute and persist it before returning. This
keeps the Week 3 demo path simple — the AM hits the URL, sees data — and
matches the eventual scheduled-snapshot path (Phase 1c §7.16) which will
just be the same generator on a cron.

Tenancy: `enforce_client_access` per §7.19 + the in-route market-belongs-to-
client check (returns 404 for cross-client market_ids to mirror the
"avoid leaking existence" rule).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from mixsight.auth.dependencies import current_user
from mixsight.db import get_db
from mixsight.models import (
    Client,
    Market,
    PacingSnapshotLine,
    PlanLine,
    ReallocationSuggestion,
    User,
)
from mixsight.pacing.reallocation import (
    compute_suggestions_for_snapshot,
    latest_suggestions_for_snapshot,
)
from mixsight.pacing.service import default_week_ending, get_or_create_snapshot
from mixsight.tenancy import enforce_client_access

router = APIRouter(prefix="/clients", tags=["pacing"])


async def _check_market_under_client(db: AsyncSession, client_id: UUID, market_id: UUID) -> Market:
    """Cross-client market lookups return 404 — mirrors §7.19 don't-leak-existence."""
    market = await db.get(Market, market_id)
    if market is None or market.client_id != client_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Market not found")
    return market


async def _resolve_currency(db: AsyncSession, client_id: UUID, market: Market) -> str:
    """Reporting currency for the response. Falls back to market local
    currency if the client hasn't set reporting_currency yet (Phase 1a
    seed leaves both as GBP for NB EMEA UK)."""
    client = await db.get(Client, client_id)
    if client and client.reporting_currency:
        return str(client.reporting_currency)
    return str(market.local_currency or "GBP")


async def _serialize_lines(db: AsyncSession, snapshot_id: UUID) -> list[dict[str, Any]]:
    """Hydrate PacingSnapshotLine rows with PlanLine labels for the UI."""
    stmt = (
        select(PacingSnapshotLine, PlanLine)
        .join(PlanLine, col(PlanLine.id) == col(PacingSnapshotLine.plan_line_id))
        .where(col(PacingSnapshotLine.snapshot_id) == snapshot_id)
    )
    rows = (await db.execute(stmt)).all()
    return [
        {
            "id": str(sl.id),
            "plan_line_id": str(sl.plan_line_id),
            "campaign_label": pl.campaign_label,
            "channel": pl.channel,
            "objective_type": sl.objective_type,
            "actual_spend_to_date": str(sl.actual_spend_to_date)
            if sl.actual_spend_to_date is not None
            else None,
            "planned_spend_to_date": str(sl.planned_spend_to_date)
            if sl.planned_spend_to_date is not None
            else None,
            "spend_drift_pct": str(sl.spend_drift_pct) if sl.spend_drift_pct is not None else None,
            "actual_kpi_to_date": str(sl.actual_kpi_to_date)
            if sl.actual_kpi_to_date is not None
            else None,
            "planned_kpi_to_date": str(sl.planned_kpi_to_date)
            if sl.planned_kpi_to_date is not None
            else None,
            "kpi_drift_pct": str(sl.kpi_drift_pct) if sl.kpi_drift_pct is not None else None,
            "status": sl.status,
            "labels": sl.labels,
        }
        for sl, pl in rows
    ]


@router.get("/{client_id}/markets/{market_id}/pacing")
async def get_pacing(
    client_id: UUID,
    market_id: UUID,
    user: User = Depends(current_user),
    _: None = Depends(enforce_client_access),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    market = await _check_market_under_client(db, client_id, market_id)
    week_ending = default_week_ending(datetime.now(UTC).date())

    snapshot = await get_or_create_snapshot(
        db,
        organization_id=user.organization_id,
        client_id=client_id,
        market_id=market_id,
        week_ending=week_ending,
    )
    await db.commit()

    if snapshot is None:
        # §7.18: "no_active_plan" empty state — return enough for the UI to
        # render the explainer banner without ambiguity.
        return {
            "snapshot": None,
            "empty_state": "no_active_plan",
            "week_ending": week_ending.isoformat(),
            "currency": await _resolve_currency(db, client_id, market),
        }

    lines = await _serialize_lines(db, snapshot.id)
    return {
        "snapshot": {
            "id": str(snapshot.id),
            "week_ending": snapshot.week_ending.isoformat(),
            "generated_at": snapshot.generated_at.isoformat() if snapshot.generated_at else None,
            "is_partial_week": snapshot.is_partial_week,
            "allocation_mode": snapshot.allocation_mode,
        },
        "lines": lines,
        "currency": await _resolve_currency(db, client_id, market),
        "empty_state": None
        if lines
        else "no_spend_in_market",  # §7.18 — plan exists, no actuals yet
    }


async def _serialize_suggestions(
    db: AsyncSession, suggestions: list[ReallocationSuggestion]
) -> list[dict[str, Any]]:
    """Hydrate donor/receiver labels for the UI."""
    line_ids = {s.donor_line_id for s in suggestions} | {s.receiver_line_id for s in suggestions}
    if not line_ids:
        return []
    label_stmt = select(PlanLine).where(col(PlanLine.id).in_(line_ids))
    labels = {pl.id: pl for pl in (await db.execute(label_stmt)).scalars().all()}
    return [
        {
            "id": str(s.id),
            "donor_line_id": str(s.donor_line_id),
            "donor_campaign_label": (
                labels[s.donor_line_id].campaign_label if s.donor_line_id in labels else None
            ),
            "receiver_line_id": str(s.receiver_line_id),
            "receiver_campaign_label": (
                labels[s.receiver_line_id].campaign_label if s.receiver_line_id in labels else None
            ),
            "proposed_amount_local": str(s.proposed_amount_local),
            "projected_delta": str(s.projected_delta) if s.projected_delta is not None else None,
            "projected_delta_units": s.projected_delta_units,
            "confidence": str(s.confidence) if s.confidence is not None else None,
            "rationale_text": s.rationale_text,
            "scope": s.scope,
        }
        for s in suggestions
    ]


@router.get("/{client_id}/markets/{market_id}/reallocation-suggestions")
async def get_reallocation_suggestions(
    client_id: UUID,
    market_id: UUID,
    user: User = Depends(current_user),
    _: None = Depends(enforce_client_access),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    await _check_market_under_client(db, client_id, market_id)
    week_ending = default_week_ending(datetime.now(UTC).date())

    snapshot = await get_or_create_snapshot(
        db,
        organization_id=user.organization_id,
        client_id=client_id,
        market_id=market_id,
        week_ending=week_ending,
    )
    await db.commit()

    if snapshot is None:
        return {
            "snapshot_id": None,
            "suggestions": [],
            "empty_state": "no_active_plan",
            "week_ending": week_ending.isoformat(),
        }

    suggestions = await latest_suggestions_for_snapshot(db, snapshot.id)
    if not suggestions:
        suggestions = await compute_suggestions_for_snapshot(db, snapshot)
        await db.commit()

    return {
        "snapshot_id": str(snapshot.id),
        "suggestions": await _serialize_suggestions(db, suggestions),
        "empty_state": None if suggestions else "insufficient_data",
    }
