"""Read-through caching adapter for the V2 provider port.

``CachingDataProvider`` is itself a :class:`DataProviderPortV2`. It fronts a
*source* provider with a :class:`MarketDataStore` cache:

* On ``fetch`` it first attempts a point-in-time read from the cache. A hit
  returns the cached frame with ``cache_hit=True`` and an as-of-preserving
  provenance — no network/IO to the source.
* On a miss (or empty coverage) it delegates to the source, and — when the
  source returns a healthy, non-empty frame — persists that frame to the cache
  for next time.

Asset identity is normalized once, up front, via
:func:`asset_uid_from_asset_id`, so the merged canonical identity model never
leaks raw ``AssetID`` objects into the storage layer (identity-isolation risk).
"""

from __future__ import annotations

from datetime import date

import pandas as pd

from indiciumforge_core.clock import utc_now_iso
from indiciumforge_core.ports.storage import (
    MarketDataStore,
    asset_uid_from_asset_id,
)
from indiciumforge_core.providers.capabilities import (
    ProviderAuthorityLevel,
)
from indiciumforge_core.providers.contracts_v2 import DataProviderPortV2
from indiciumforge_core.providers.query import DataQuery
from indiciumforge_core.providers.result import (
    ProviderFailureStatus,
    ProviderProvenance,
    ProviderResult,
)


class CachingDataProvider:
    """A ``DataProviderPortV2`` that caches successful fetches in a store."""

    def __init__(
        self,
        source: DataProviderPortV2,
        store: MarketDataStore,
        *,
        cache_policy: str = "read_through",
        cache_only: bool = False,
    ) -> None:
        self._source = source
        self._store = store
        self._cache_policy = cache_policy
        # When True, a cache miss is NOT delegated to the source — the caller
        # (a read-only workflow consumer) gets an EMPTY result with a warning
        # instead of a hidden network fetch. Explicit ``sync``/backfill CLI
        # commands construct the cache with ``cache_only=False`` so they can
        # populate the store. This enforces the "read-only consumer vs explicit
        # sync" invariant borrowed from the indiciumgrid reference design.
        self._cache_only = cache_only
        # Advertise ourselves as a cache front-end to the source.
        self.provider_id = f"cache[{getattr(source, 'provider_id', 'source')}]"
        self.authority_level = getattr(
            source, "authority_level", ProviderAuthorityLevel.FALLBACK
        )
        self.capabilities = tuple(getattr(source, "capabilities", ()))

    # -- DataProviderPortV2 surface -------------------------------------------
    def supports_query(self, query: DataQuery) -> bool:
        return self._source.supports_query(query)

    def fetch(self, query: DataQuery) -> ProviderResult:
        asset_uid = asset_uid_from_asset_id(query.asset)

        # 1) Probe the cache (point-in-time aware).
        cached_frame, cached_prov = self._store.fetch_ohlcv(
            asset_uid,
            start=query.start,
            end=query.end,
            as_of=query.as_of,
        )
        if not cached_frame.empty:
            return ProviderResult(
                frame=cached_frame.reset_index(drop=True),
                provenance=self._cache_provenance(query, cached_prov),
            )

        # 2) Cache miss — delegate to the source (unless cache_only).
        if self._cache_only:
            return ProviderResult(
                frame=pd.DataFrame(),
                provenance=ProviderProvenance(
                    provider_id=self.provider_id,
                    authority_level=self.authority_level,
                    data_kind=query.data_kind,
                    asset_domain=query.asset_domain,
                    captured_at=utc_now_iso(),
                    as_of=query.as_of,
                    cache_hit=False,
                    cache_policy=self._cache_policy,
                    failure_status=ProviderFailureStatus.EMPTY,
                    warnings=(
                        "cache_only: miss, not fetching source",
                    ),
                    session_model=query.session_model,
                    checkpoint_id=query.checkpoint_id,
                    cycle_id=query.cycle_id,
                ),
            )

        result = self._source.fetch(query)
        frame = result.frame

        # 3) Persist healthy, non-empty results (skip empties/failures).
        if (
            not frame.empty
            and result.provenance.failure_status == ProviderFailureStatus.OK
        ):
            self._store.write_ohlcv(asset_uid, frame, provenance=result.provenance)

        return result

    # -- provenance bookkeeping ------------------------------------------------
    def _cache_provenance(
        self, query: DataQuery, cached: object
    ) -> ProviderProvenance:
        """Build a ``ProviderProvenance`` describing a cache hit.

        ``cached`` is the domain ``Provenance`` returned by the store; we carry
        its as-of date and warnings forward so consumers keep point-in-time
        semantics intact.
        """
        as_of: date | None = getattr(cached, "as_of", None)
        warnings = tuple(getattr(cached, "warnings", ()) or ())
        return ProviderProvenance(
            provider_id=self.provider_id,
            authority_level=self.authority_level,
            data_kind=query.data_kind,
            asset_domain=query.asset_domain,
            captured_at=utc_now_iso(),
            as_of=as_of,
            cache_hit=True,
            cache_policy=self._cache_policy,
            session_model=query.session_model,
            checkpoint_id=query.checkpoint_id,
            cycle_id=query.cycle_id,
            warnings=warnings,
        )


# Mark as a structural subtype of the port.
DataProviderPortV2.register(CachingDataProvider)
