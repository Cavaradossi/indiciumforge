"""Golden A-share snapshot provider.

``GoldenSnapshotProvider`` serves a *committed* parquet panel of real A-share
OHLCV so that CI, tests, and the paper's §9 case study run **offline and
deterministically** — independent of akshare's network flakiness or schema
drift. It is a :class:`DataProviderPortV2` with ``FIXTURE`` authority, structurally
identical to :class:`LocalFixtureProviderV2` but reading a single long-format
parquet panel instead of per-asset CSVs.

The snapshot is produced once by ``scripts/snapshot_golden_ashare.py`` (a manual,
non-CI step) and committed under ``tests/fixtures/golden_ashare/panel.parquet``.
Its schema (``asset_uid, date, open, high, low, close, volume``) reuses the
canonical :data:`OHLCV_COLUMNS` plus an ``asset_uid`` key matching
``AssetID.uid`` (``"sse:stock:600000"``).

Point-in-time semantics are honored: when ``query.as_of`` is set, rows with
``date > as_of`` are excluded, mirroring the storage layer's two-guard filter.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pandas as pd

from indiciumforge_core.clock import utc_now_iso
from indiciumforge_core.ports.storage import asset_uid_from_asset_id
from indiciumforge_core.providers.capabilities import (
    DataKind,
    LatencyProfile,
    ProviderAuthorityLevel,
    ProviderCapability,
)
from indiciumforge_core.providers.contracts_v2 import DataProviderPortV2
from indiciumforge_core.providers.query import DataQuery
from indiciumforge_core.providers.result import (
    ProviderFailureStatus,
    ProviderProvenance,
    ProviderResult,
)
from indiciumforge_core.workflow.model import AssetDomain

_PANEL_COLUMNS = ("asset_uid", "date", "open", "high", "low", "close", "volume")


def _require_pyarrow() -> None:
    try:
        import pyarrow  # noqa: F401  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - only without the storage extra
        raise ImportError(
            "pyarrow is required to read the golden snapshot. Install the storage "
            "extra: pip install 'indiciumforge-core[storage]'"
        ) from exc


class GoldenSnapshotProvider:
    """A ``DataProviderPortV2`` serving a committed golden A-share parquet panel."""

    provider_id = "golden_ashare"
    authority_level = ProviderAuthorityLevel.FIXTURE
    capabilities = (
        ProviderCapability(
            asset_domain=AssetDomain.CHINA_A_SHARE,
            data_kind=DataKind.OHLCV,
            latency_profile=LatencyProfile.HISTORICAL,
            venues=("sse", "szse", "bse_cn"),
        ),
    )

    def __init__(self, panel_path: Path | str) -> None:
        self._panel_path = Path(panel_path)
        self._panel: pd.DataFrame | None = None  # lazy load

    # -- lazy load ------------------------------------------------------------
    def _load(self) -> pd.DataFrame:
        if self._panel is None:
            _require_pyarrow()
            if not self._panel_path.is_file():
                raise FileNotFoundError(
                    f"golden snapshot not found: {self._panel_path}"
                )
            df = pd.read_parquet(self._panel_path)
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"]).dt.date
            self._panel = df
        return self._panel

    @property
    def available_uids(self) -> tuple[str, ...]:
        panel = self._load()
        return tuple(panel["asset_uid"].unique()) if "asset_uid" in panel.columns else ()

    # -- DataProviderPortV2 surface -------------------------------------------
    def supports_query(self, query: DataQuery) -> bool:
        if query.data_kind != DataKind.OHLCV:
            return False
        if query.asset_domain != AssetDomain.CHINA_A_SHARE:
            return False
        uid = asset_uid_from_asset_id(query.asset)
        return uid in self.available_uids

    def fetch(self, query: DataQuery) -> ProviderResult:
        uid = asset_uid_from_asset_id(query.asset)
        panel = self._load()

        mask = panel["asset_uid"] == uid
        if query.start is not None:
            mask &= panel["date"] >= query.start
        if query.end is not None:
            mask &= panel["date"] <= query.end
        if query.as_of is not None:
            # Point-in-time: never expose rows strictly after as_of.
            mask &= panel["date"] <= query.as_of

        frame = panel.loc[mask, list(_PANEL_COLUMNS[1:])].copy()

        if frame.empty:
            if uid not in self.available_uids:
                failure = ProviderFailureStatus.MISSING_CAPABILITY
                warn = (f"asset {uid} not in golden snapshot",)
            else:
                failure = ProviderFailureStatus.EMPTY
                warn = ("no rows in the requested date range",)
            return ProviderResult(
                frame=pd.DataFrame(columns=list(_PANEL_COLUMNS[1:])),
                provenance=self._provenance(
                    query, failure_status=failure, warnings=warn
                ),
            )

        as_of = frame["date"].iloc[-1]
        if not isinstance(as_of, date):
            as_of = pd.to_datetime(as_of).date()

        return ProviderResult(
            frame=frame.sort_values("date").reset_index(drop=True),
            provenance=self._provenance(query, as_of=as_of),
        )

    # -- provenance -----------------------------------------------------------
    def _provenance(
        self,
        query: DataQuery,
        *,
        as_of: date | None = None,
        failure_status: ProviderFailureStatus = ProviderFailureStatus.OK,
        warnings: tuple[str, ...] = (),
    ) -> ProviderProvenance:
        return ProviderProvenance(
            provider_id=self.provider_id,
            authority_level=self.authority_level,
            data_kind=query.data_kind,
            asset_domain=query.asset_domain,
            captured_at=utc_now_iso(),
            as_of=as_of or query.as_of,
            cache_hit=True,
            cache_policy="read_through_fixture",
            failure_status=failure_status,
            session_model=query.session_model,
            checkpoint_id=query.checkpoint_id,
            cycle_id=query.cycle_id,
            warnings=warnings,
        )


# Mark as a structural subtype of the port.
DataProviderPortV2.register(GoldenSnapshotProvider)
