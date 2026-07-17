from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from pathlib import Path


class MissingData(Exception):
    """Raised when a provider cannot return data for a request."""


# ---------------------------------------------------------------------------
# Exchange: extensible value object + registry.
#
# Previously a 3-member A-share-only ``str, Enum`` (SSE/SZSE/BSE_CN), which
# hard-wired the domain model to a single market and violated the open/closed
# principle for a "global quant framework" (see ADR-0024). Exchanges are now
# *data*: well-known venues are seeded in a module-level registry, but any
# non-empty code is accepted at runtime so the model is market-agnostic.
# ---------------------------------------------------------------------------
_EXCHANGE_REGISTRY: dict[str, "Exchange"] = {}


@dataclass(frozen=True)
class Exchange:
    """A trading venue identified by a canonical lowercase ``code`` (e.g. ``"sse"``).

    ``name`` is a human label, ``region`` an ISO-3166 alpha-2 code (``"UNKNOWN"``
    for ad-hoc venues), and ``mic`` the optional ISO 10383 market identifier.
    """

    code: str
    name: str
    region: str
    mic: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "code", self.code.lower())

    @property
    def value(self) -> str:
        """Canonical lowercase code; kept for serialization parity with the old enum."""
        return self.code

    def __str__(self) -> str:
        return self.code

    @classmethod
    def register(
        cls, code: str, name: str, region: str, mic: str = ""
    ) -> "Exchange":
        """Register a known exchange and return its canonical (shared) instance."""
        ex = cls(code=code, name=name, region=region, mic=mic)
        _EXCHANGE_REGISTRY[ex.code] = ex
        return ex

    @classmethod
    def from_code(cls, code: str) -> "Exchange":
        """Resolve an exchange by code; returns an ad-hoc instance for unknown codes."""
        if not code:
            raise ValueError("exchange code must be a non-empty string")
        code = code.lower()
        if code in _EXCHANGE_REGISTRY:
            return _EXCHANGE_REGISTRY[code]
        return cls(code=code, name=code.upper(), region="UNKNOWN")


# Seeded exchanges — a curated registry, deliberately not exhaustive.
SSE = Exchange.register("sse", "Shanghai Stock Exchange", "CN", "XSHG")
SZSE = Exchange.register("szse", "Shenzhen Stock Exchange", "CN", "XSHE")
BSE_CN = Exchange.register("bse_cn", "Beijing Stock Exchange", "CN", "XBJH")
XNAS = Exchange.register("xnas", "NASDAQ", "US", "XNAS")
XNYS = Exchange.register("xnys", "New York Stock Exchange", "US", "XNYS")
XLON = Exchange.register("xlon", "London Stock Exchange", "GB", "XLON")
XTKS = Exchange.register("xtks", "Tokyo Stock Exchange", "JP", "XTKS")
XHKG = Exchange.register("xhkg", "Hong Kong Stock Exchange", "HK", "XHKG")

# Backward-compatible attribute access (``Exchange.SSE``) for existing callers/tests.
Exchange.SSE = SSE
Exchange.SZSE = SZSE
Exchange.BSE_CN = BSE_CN

# Seed list for the A-share recipe — a convenience slice, not the whole model.
A_SHARE_EXCHANGES: tuple[Exchange, ...] = (SSE, SZSE, BSE_CN)


class AssetType(str, Enum):
    STOCK = "stock"
    ETF = "etf"
    INDEX = "index"
    OTHER = "other"


@dataclass(frozen=True)
class AssetID:
    """Canonical asset identity.

    ``uid`` is ``exchange_code:asset_type:code`` and is stable across runs.
    ``currency`` is intentionally empty by default and must be populated by the
    data provider — the domain model no longer assumes a single settlement
    currency (CNY) for every asset (see ADR-0024).
    """

    code: str
    exchange: Exchange
    asset_type: AssetType = AssetType.STOCK
    currency: str = ""

    @property
    def uid(self) -> str:
        return f"{self.exchange.value}:{self.asset_type.value}:{self.code}"


# Deprecated alias retained for one release; new code must use :class:`AssetID`.
AssetId = AssetID


@dataclass(frozen=True)
class Provenance:
    provider: str
    tier: str = "unknown"
    as_of: date | None = None
    fetched_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    )
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class RunContext:
    trade_date: date
    artifact_root: Path
    run_id: str = "default"
    started_at: str = ""


@dataclass(frozen=True)
class IndiciumForgeWarning:
    code: str
    message: str
    severity: str = "warning"


@dataclass(frozen=True)
class ResultEnvelope:
    status: str
    warnings: tuple[IndiciumForgeWarning, ...] = field(default_factory=tuple)
