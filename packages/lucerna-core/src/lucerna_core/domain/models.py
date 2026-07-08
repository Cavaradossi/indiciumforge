from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from pathlib import Path


class MissingData(Exception):
    """Raised when a provider cannot return data for a request."""


class Exchange(str, Enum):
    SSE = "sse"
    SZSE = "szse"
    BSE_CN = "bse_cn"


class AssetType(str, Enum):
    STOCK = "stock"
    ETF = "etf"
    INDEX = "index"
    OTHER = "other"


@dataclass(frozen=True)
class AssetID:
    code: str
    exchange: Exchange
    asset_type: AssetType = AssetType.STOCK
    currency: str = "CNY"

    @property
    def uid(self) -> str:
        return f"{self.exchange.value}:{self.asset_type.value}:{self.code}"


@dataclass(frozen=True)
class AssetId:
    code: str
    market: str
    asset_type: AssetType = AssetType.STOCK
    currency: str = ""

    @property
    def uid(self) -> str:
        return f"{self.market}:{self.code}"


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
    run_id: str = ""


@dataclass(frozen=True)
class LucernaWarning:
    code: str
    message: str
    severity: str = "warning"


@dataclass(frozen=True)
class ResultEnvelope:
    status: str
    warnings: tuple[LucernaWarning, ...] = field(default_factory=tuple)
