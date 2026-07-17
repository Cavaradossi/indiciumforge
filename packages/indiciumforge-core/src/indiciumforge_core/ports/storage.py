from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import TYPE_CHECKING, Any, Protocol

import pandas as pd

from indiciumforge_core.domain.models import AssetID, Provenance
from indiciumforge_core.ports.contracts import FetchResult

if TYPE_CHECKING:
    from indiciumforge_core.providers.result import ProviderProvenance

__all__ = [
    "MarketDataStore",
    "MetadataStore",
    "RunRecord",
    "StageRecord",
    "FactorMetaRecord",
    "ParityReportRecord",
    "asset_uid_from_asset_id",
]


# ---------------------------------------------------------------------------
# Market data layer (time-series OHLCV, point-in-time aware)
# ---------------------------------------------------------------------------
class MarketDataStore(Protocol):
    """Time-series OHLCV storage with point-in-time semantics.

    Implementations persist per-asset frames and must honour ``as_of`` on read:
    only rows whose trade ``date`` and ``provenance_as_of`` are ``<= as_of`` are
    returned, and duplicate trade dates are de-duplicated to the latest captured
    snapshot (see ADR-0025). ``asset`` arguments are the canonical ``asset_uid``
    string (``exchange:asset_type:code``), not the ``AssetID`` object.
    """

    def write_ohlcv(
        self, asset_uid: str, frame: pd.DataFrame, *, provenance: ProviderProvenance
    ) -> None: ...

    def fetch_ohlcv(
        self,
        asset_uid: str,
        *,
        start: date | None = None,
        end: date | None = None,
        as_of: date | None = None,
    ) -> FetchResult: ...

    def fetch_ohlcv_batch(
        self,
        asset_uids: list[str],
        *,
        start: date | None = None,
        end: date | None = None,
        as_of: date | None = None,
    ) -> dict[str, FetchResult]: ...

    def fetch_panel(
        self,
        asset_uids: list[str],
        *,
        start: date,
        end: date,
        as_of: date | None = None,
    ) -> pd.DataFrame: ...

    def has_coverage(self, asset_uid: str, *, start: date, end: date) -> bool: ...


# ---------------------------------------------------------------------------
# Metadata layer (relational: runs / stages / factor meta / parity reports)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class RunRecord:
    run_id: str
    recipe_id: str
    asset_domain: str
    session_model: str
    cycle_id: str
    trade_date: str
    started_at: str
    status: str = "ok"
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StageRecord:
    stage_id: str
    run_id: str
    recipe_id: str
    trade_date: str
    status: str
    input_descriptor_hash: str
    output_content_hash: str
    provider_id: str | None = None
    warnings: tuple[str, ...] = ()
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FactorMetaRecord:
    factor_id: str
    name: str
    asset_domain: str
    version: str
    description: str = ""
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ParityReportRecord:
    report_id: str
    run_id: str
    dimension: str
    status: str
    summary: dict[str, Any] = field(default_factory=dict)
    generated_at: str = ""


class MetadataStore(Protocol):
    """Relational metadata store for runs, stages, factors and parity reports."""

    def record_run(self, run: RunRecord) -> None: ...

    def get_run(self, run_id: str) -> RunRecord | None: ...

    def list_runs(
        self,
        *,
        trade_date: date | str | None = None,
        recipe_id: str | None = None,
    ) -> list[RunRecord]: ...

    def record_stage(self, stage: StageRecord) -> None: ...

    def find_stage_by_input_hash(
        self,
        *,
        recipe_id: str,
        stage_id: str,
        trade_date: str,
        input_descriptor_hash: str,
    ) -> StageRecord | None: ...

    def record_factor_metadata(self, rec: FactorMetaRecord) -> None: ...

    def record_parity_report(self, rec: ParityReportRecord) -> None: ...


def asset_uid_from_asset_id(asset: AssetID) -> str:
    """Normalize an ``AssetID`` to the canonical ``asset_uid`` used by stores.

    Centralizes the ``exchange:asset_type:code`` convention so callers (and the
    W1-merged identity model) don't hard-code the uid format at every call site.
    """
    return asset.uid
