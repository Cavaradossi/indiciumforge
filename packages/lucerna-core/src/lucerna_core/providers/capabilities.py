from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from lucerna_core.workflow.model import AssetDomain


class ProviderAuthorityLevel(str, Enum):
    PRIMARY = "primary"
    FALLBACK = "fallback"
    CROSS_CHECK = "cross_check"
    EXPERIMENTAL = "experimental"
    FIXTURE = "fixture"


class DataKind(str, Enum):
    OHLCV = "ohlcv"
    QUOTE_SNAPSHOT = "quote_snapshot"
    MARKET_BREADTH = "market_breadth"
    FUNDAMENTALS = "fundamentals"
    FUNDING_RATE = "funding_rate"
    OPEN_INTEREST = "open_interest"
    OPTIONS_CHAIN = "options_chain"
    LIQUIDATION_EVENTS = "liquidation_events"


class LatencyProfile(str, Enum):
    HISTORICAL = "historical"
    DELAYED = "delayed"
    NEAR_REALTIME = "near_realtime"
    REALTIME = "realtime"
    ROLLING_24X7 = "rolling_24x7"


@dataclass(frozen=True)
class ProviderCapability:
    asset_domain: AssetDomain
    data_kind: DataKind
    latency_profile: LatencyProfile
    venues: tuple[str, ...] = ()

    def matches(
        self,
        *,
        asset_domain: AssetDomain,
        data_kind: DataKind,
        venue: str | None = None,
    ) -> bool:
        if self.asset_domain != asset_domain or self.data_kind != data_kind:
            return False
        if self.venues and venue is not None and venue not in self.venues:
            return False
        return True
