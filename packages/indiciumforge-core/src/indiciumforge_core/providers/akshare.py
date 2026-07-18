"""akshare data provider for A-share OHLCV.

``AkshareDataProvider`` is a :class:`DataProviderPortV2` adapter that fetches
daily OHLCV for China A-shares via the `akshare <https://akshare.akfamily.xyz/>`_
library (MIT, no API token required). It is the framework's first *real*
network data source — every prior provider read synthetic fixtures.

akshare is a lazy, opt-in dependency: importing this module does **not** import
akshare. The first ``fetch`` call triggers ``_require_akshare()``, which raises
a helpful ``ImportError`` pointing at ``pip install indiciumforge-core[data]``
if the extra is not installed. This keeps the core package importable without
the (transitively heavy) akshare dependency tree.

Composition with the cache::

    CachingDataProvider(
        source=AkshareDataProvider(),
        store=ParquetDuckDBMarketDataStore(root),
    )

gives point-in-time offline reuse for free: the first fetch hits the network and
persists to parquet; subsequent reads are cache hits.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import date

import pandas as pd

from indiciumforge_core.clock import utc_now_iso
from indiciumforge_core.domain.models import AssetID, AssetType, Exchange
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

# akshare returns Chinese column names; map to the canonical OHLCV schema.
_AKSHARE_COLUMN_MAP: dict[str, str] = {
    "日期": "date",
    "开盘": "open",
    "收盘": "close",
    "最高": "high",
    "最低": "low",
    "成交量": "volume",
}


def _require_akshare() -> object:
    try:
        import akshare  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - exercised only without the extra
        raise ImportError(
            "akshare is not installed. Install the data extra: "
            "pip install 'indiciumforge-core[data]'"
        ) from exc
    return akshare


def _exchange_for_code(code: str) -> Exchange:
    """Map an A-share numeric code to its exchange (SSE/SZSE/BSE_CN)."""
    if not code:
        raise ValueError("asset code must be non-empty")
    first = code[0]
    if first == "6":
        return Exchange.from_code("sse")
    if first in ("0", "3"):
        return Exchange.from_code("szse")
    if first in ("8", "4"):
        return Exchange.from_code("bse_cn")
    # Unknown prefix — default to SSE as an ad-hoc venue.
    return Exchange.from_code("sse")


class AkshareDataProvider:
    """A ``DataProviderPortV2`` fetching A-share daily OHLCV via akshare."""

    provider_id = "akshare"
    authority_level = ProviderAuthorityLevel.PRIMARY
    capabilities = (
        ProviderCapability(
            asset_domain=AssetDomain.CHINA_A_SHARE,
            data_kind=DataKind.OHLCV,
            latency_profile=LatencyProfile.DELAYED,
            venues=("sse", "szse", "bse_cn"),
        ),
    )

    def __init__(
        self,
        *,
        adjust: str = "qfq",
        secret_resolver: Callable[[str], str | None] | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._adjust = adjust  # ""不复权 / "qfq"前复权 / "hfq"后复权
        self._secret_resolver = secret_resolver  # akshare needs no token; seam for parity
        self._timeout = timeout

    # -- DataProviderPortV2 surface -------------------------------------------
    def supports_query(self, query: DataQuery) -> bool:
        if query.data_kind != DataKind.OHLCV:
            return False
        if query.asset_domain != AssetDomain.CHINA_A_SHARE:
            return False
        return query.asset.code.isdigit()

    def fetch(self, query: DataQuery) -> ProviderResult:
        if not self.supports_query(query):
            return ProviderResult(
                frame=pd.DataFrame(),
                provenance=self._provenance(
                    query,
                    failure_status=ProviderFailureStatus.MISSING_CAPABILITY,
                    warnings=("unsupported query for akshare",),
                ),
            )

        code = query.asset.code
        start = query.start.strftime("%Y%m%d") if query.start else "20100101"
        end = query.end.strftime("%Y%m%d") if query.end else date.today().strftime("%Y%m%d")

        try:
            ak = _require_akshare()
            raw = ak.stock_zh_a_hist(  # type: ignore[attr-defined]
                symbol=code,
                period="daily",
                start_date=start,
                end_date=end,
                adjust=self._adjust or "",
            )
        except Exception as exc:
            return ProviderResult(
                frame=pd.DataFrame(),
                provenance=self._provenance(
                    query,
                    failure_status=ProviderFailureStatus.PROVIDER_ERROR,
                    warnings=(f"akshare fetch error: {exc}",),
                ),
            )

        frame = self._normalize(raw)
        if frame.empty:
            return ProviderResult(
                frame=frame,
                provenance=self._provenance(
                    query,
                    failure_status=ProviderFailureStatus.EMPTY,
                    warnings=("akshare returned no rows for the date range",),
                ),
            )

        as_of = frame["date"].iloc[-1]
        if not isinstance(as_of, date):
            as_of = pd.to_datetime(as_of).date()

        return ProviderResult(
            frame=frame.reset_index(drop=True),
            provenance=self._provenance(query, as_of=as_of),
        )

    # -- helpers --------------------------------------------------------------
    @staticmethod
    def _normalize(raw: pd.DataFrame) -> pd.DataFrame:
        if raw is None or raw.empty:
            return pd.DataFrame(columns=list(_AKSHARE_COLUMN_MAP.values()))
        # Rename only the columns we recognize; drop the rest.
        renamed = raw.rename(columns=_AKSHARE_COLUMN_MAP)
        keep = [
            c
            for c in ("date", "open", "high", "low", "close", "volume")
            if c in renamed.columns
        ]
        frame = renamed[keep].copy()
        frame["date"] = pd.to_datetime(frame["date"]).dt.date
        for col in ("open", "high", "low", "close"):
            if col in frame.columns:
                frame[col] = pd.to_numeric(frame[col], errors="coerce")
        if "volume" in frame.columns:
            frame["volume"] = pd.to_numeric(frame["volume"], errors="coerce").fillna(0)
        frame = frame.dropna(subset=["open", "high", "low", "close"], how="all")
        frame = frame.sort_values("date").reset_index(drop=True)
        return frame

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
            cache_hit=False,
            cache_policy="none",
            quota_policy="none",
            failure_status=failure_status,
            session_model=query.session_model,
            checkpoint_id=query.checkpoint_id,
            cycle_id=query.cycle_id,
            warnings=warnings,
        )

    @staticmethod
    def asset_from_code(code: str) -> AssetID:
        """Build an :class:`AssetID` for an A-share numeric code."""
        return AssetID(
            code=code,
            exchange=_exchange_for_code(code),
            asset_type=AssetType.STOCK,
            currency="CNY",
        )


# Mark as a structural subtype of the port.
DataProviderPortV2.register(AkshareDataProvider)
