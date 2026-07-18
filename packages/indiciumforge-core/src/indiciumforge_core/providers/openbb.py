"""OpenBB data provider for global (US-equity first) OHLCV.

``OpenBBDataProvider`` is a :class:`DataProviderPortV2` adapter that fetches
daily OHLCV via the `OpenBB Platform <https://github.com/OpenBB-finance/OpenBB>`_
(``pip install openbb``, Apache-2.0). It is the framework's first *global,
non-A-share* real data source and backs the public OpenBB demo (see
``docs/decisions/ADR-0027-openbb-adapter-boundary-v2.1.md``).

Network is strictly opt-in. Importing this module does **not** import openbb.
The first ``fetch`` call triggers ``_require_openbb()``, which raises a helpful
``ImportError`` pointing at ``pip install indiciumforge-core[openbb]`` if the
extra is not installed. The offline public demo does **not** use this provider
at all — it reads a committed deterministic sample panel — so default CI never
touches the network (ADR-0019 rule 7: no hidden network fetch).

Composition with the cache is identical to the akshare adapter::

    CachingDataProvider(
        source=OpenBBDataProvider(),
        store=ParquetDuckDBMarketDataStore(root),
    )
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

# OpenBB historical frames expose lowercase OHLCV columns already; this map keeps
# the normalization explicit and tolerant of an index-vs-column ``date``.
_OPENBB_COLUMN_MAP: dict[str, str] = {
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "volume": "volume",
}


def _require_openbb() -> object:
    try:
        from openbb import obb  # type: ignore[import-not-found]
    except ImportError as exc:  # pragma: no cover - exercised only without the extra
        raise ImportError(
            "openbb is not installed. Install the openbb extra: "
            "pip install 'indiciumforge-core[openbb]'"
        ) from exc
    return obb


class OpenBBDataProvider:
    """A ``DataProviderPortV2`` fetching US-equity daily OHLCV via OpenBB."""

    provider_id = "openbb"
    authority_level = ProviderAuthorityLevel.PRIMARY
    capabilities = (
        ProviderCapability(
            asset_domain=AssetDomain.US_EQUITY,
            data_kind=DataKind.OHLCV,
            latency_profile=LatencyProfile.DELAYED,
            venues=("xnas", "xnys"),
        ),
    )

    def __init__(
        self,
        *,
        openbb_provider: str = "yfinance",
        secret_resolver: Callable[[str], str | None] | None = None,
        timeout: float = 30.0,
    ) -> None:
        # OpenBB routes to a concrete data vendor; yfinance needs no API key,
        # keeping the demo token-free. Other vendors resolve keys via OpenBB's
        # own credential store, never a hardcoded path here.
        self._openbb_provider = openbb_provider
        self._secret_resolver = secret_resolver
        self._timeout = timeout

    # -- DataProviderPortV2 surface -------------------------------------------
    def supports_query(self, query: DataQuery) -> bool:
        if query.data_kind != DataKind.OHLCV:
            return False
        if query.asset_domain != AssetDomain.US_EQUITY:
            return False
        # US tickers are alphabetic (optionally with a dot class suffix).
        return query.asset.code.replace(".", "").isalpha()

    def fetch(self, query: DataQuery) -> ProviderResult:
        if not self.supports_query(query):
            return ProviderResult(
                frame=pd.DataFrame(),
                provenance=self._provenance(
                    query,
                    failure_status=ProviderFailureStatus.MISSING_CAPABILITY,
                    warnings=("unsupported query for openbb",),
                ),
            )

        symbol = query.asset.code.upper()
        start = query.start.isoformat() if query.start else "2010-01-01"
        end = query.end.isoformat() if query.end else date.today().isoformat()

        try:
            obb = _require_openbb()
            raw = obb.equity.price.historical(  # type: ignore[attr-defined]
                symbol=symbol,
                start_date=start,
                end_date=end,
                provider=self._openbb_provider,
            )
            frame_in = self._to_frame(raw)
        except Exception as exc:
            return ProviderResult(
                frame=pd.DataFrame(),
                provenance=self._provenance(
                    query,
                    failure_status=ProviderFailureStatus.PROVIDER_ERROR,
                    warnings=(f"openbb fetch error: {exc}",),
                ),
            )

        frame = self._normalize(frame_in)
        if frame.empty:
            return ProviderResult(
                frame=frame,
                provenance=self._provenance(
                    query,
                    failure_status=ProviderFailureStatus.EMPTY,
                    warnings=("openbb returned no rows for the date range",),
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
    def _to_frame(raw: object) -> pd.DataFrame:
        """Coerce an OpenBB result object (OBBject) or DataFrame into a frame.

        OpenBB returns an ``OBBject`` exposing ``.to_dataframe()``; tests inject a
        plain DataFrame. Both are supported without importing openbb types.
        """
        if isinstance(raw, pd.DataFrame):
            return raw
        to_df = getattr(raw, "to_dataframe", None)
        if callable(to_df):
            return to_df()
        results = getattr(raw, "results", None)
        if results is not None:
            return pd.DataFrame([dict(r) for r in results])
        raise TypeError(f"unsupported openbb result type: {type(raw)!r}")

    @staticmethod
    def _normalize(raw: pd.DataFrame) -> pd.DataFrame:
        if raw is None or raw.empty:
            return pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])
        frame = raw.copy()
        # OpenBB usually returns a DatetimeIndex named 'date'; promote it.
        if "date" not in frame.columns:
            frame = frame.reset_index()
            if "date" not in frame.columns and "index" in frame.columns:
                frame = frame.rename(columns={"index": "date"})
        frame = frame.rename(columns=_OPENBB_COLUMN_MAP)
        keep = [
            c
            for c in ("date", "open", "high", "low", "close", "volume")
            if c in frame.columns
        ]
        frame = frame[keep].copy()
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
    def asset_from_ticker(ticker: str, *, exchange: str = "xnas") -> AssetID:
        """Build an :class:`AssetID` for a US-equity ticker (defaults to NASDAQ)."""
        if not ticker:
            raise ValueError("ticker must be non-empty")
        return AssetID(
            code=ticker.upper(),
            exchange=Exchange.from_code(exchange),
            asset_type=AssetType.STOCK,
            currency="USD",
        )


# Mark as a structural subtype of the port.
DataProviderPortV2.register(OpenBBDataProvider)
