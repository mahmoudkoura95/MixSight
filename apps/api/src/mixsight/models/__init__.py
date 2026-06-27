"""ORM models — every table-bearing module is imported here so SQLModel.metadata
sees them at Alembic autogenerate time.
"""

from mixsight.models.actuals import Actuals
from mixsight.models.ad_account_mapping import AdAccountMapping
from mixsight.models.audit_log import AuditLog
from mixsight.models.campaign_label_rule import CampaignLabelRule
from mixsight.models.client import Client
from mixsight.models.client_taxonomy import ClientTaxonomy
from mixsight.models.connector_auth import ConnectorAuth
from mixsight.models.connector_auth_event import ConnectorAuthEvent
from mixsight.models.connector_pull import ConnectorPull
from mixsight.models.contribution_fit import ContributionFit
from mixsight.models.defense_kit import DefenseKit
from mixsight.models.encrypted_secret import EncryptedSecret
from mixsight.models.forecast_run import ForecastRun
from mixsight.models.incrementality_result import IncrementalityResult
from mixsight.models.macro_signal import MacroSignal
from mixsight.models.market import Market
from mixsight.models.market_config import MarketConfig
from mixsight.models.organization import Organization
from mixsight.models.pacing_snapshot import PacingSnapshot, PacingSnapshotLine
from mixsight.models.plan import Plan
from mixsight.models.plan_line import PlanLine
from mixsight.models.promotional_event import PromotionalEvent
from mixsight.models.reallocation_suggestion import ReallocationSuggestion
from mixsight.models.recommendation_log import RecommendationLog
from mixsight.models.reconciliation_factor import ReconciliationFactor
from mixsight.models.user import User
from mixsight.models.user_client_access import UserClientAccess

__all__ = [
    "Actuals",
    "AdAccountMapping",
    "AuditLog",
    "CampaignLabelRule",
    "Client",
    "ClientTaxonomy",
    "ConnectorAuth",
    "ConnectorAuthEvent",
    "ConnectorPull",
    "ContributionFit",
    "DefenseKit",
    "EncryptedSecret",
    "ForecastRun",
    "IncrementalityResult",
    "MacroSignal",
    "Market",
    "MarketConfig",
    "Organization",
    "PacingSnapshot",
    "PacingSnapshotLine",
    "Plan",
    "PlanLine",
    "PromotionalEvent",
    "ReallocationSuggestion",
    "RecommendationLog",
    "ReconciliationFactor",
    "User",
    "UserClientAccess",
]
