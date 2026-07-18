"""Time-series OHLCV store backed by partitioned Parquet, queried via DuckDB.

This module implements :class:`~indiciumforge_core.ports.storage.MarketDataStore`.
It is **opt-in**: DuckDB and PyArrow are only imported on first use, so the
core package keeps zero hard third-party dependencies. Install them with the
``storage`` extra (``pip install indiciumforge-core[storage]``).

Design notes (also recorded in ADR-0025):

* Partition layout is Hive-style for free partition-pruning by year::

      <root>/ohlcv/<exchange>/<asset_type>/<code>/year=<YYYY>/part-<uid>.parquet

* **Point-in-time correctness.** Reads apply two guards to prevent
  look-ahead bias, matching the point-in-time correctness spec exactly:

    - ``date <= as_of`` — only trade rows known as of the snapshot date;
    - ``provenance_as_of <= as_of`` — the snapshot's own as-of (the last trade
      date it represents) must already be on/before ``as_of``.

  (A ``captured_at`` *physical-timestamp* guard is deliberately **not** applied
  as a hard filter: a live cache populated "now" legitimately carries a capture
  time after the trade date, and excluding it would void the cache. The
  ``captured_at`` column is still persisted and used for de-duplication only.)

* **De-duplication.** Overlapping writes (e.g. a re-run that re-emits a date
  range) leave multiple rows per ``date``; the read keeps the single latest
  valid snapshot via
  ``ROW_NUMBER() OVER (PARTITION BY date ORDER BY p_captured_at DESC)``.
"""

from __future__ import annotations

import json
import uuid
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from indiciumforge_core.domain.models import Provenance
from indiciumforge_core.ports.contracts import OHLCV_COLUMNS, FetchResult
from indiciumforge_core.ports.storage import MarketDataStore
from indiciumforge_core.providers.result import ProviderProvenance

# Provenance columns persisted alongside the OHLCV rows so each snapshot can be
# reconstructed and point-in-time filtered. Prefixed to avoid clashing with any
# user frame columns.
_PROV_COLUMNS = (
    "p_provider",
    "p_tier",
    "p_as_of",
    "p_captured_at",
    "p_warnings",
    "p_payload",
)


def _require_storage_deps() -> tuple[Any, Any]:
    """Lazily import duckdb + pyarrow; raise a helpful error if absent."""
    try:  # pragma: no cover - import side-effects only
        import duckdb  # noqa: F401
        import pyarrow as pa  # noqa: F401
        import pyarrow.parquet as pq  # noqa: F401
    except ImportError as exc:  # pragma: no cover - depends on install
        raise ImportError(
            "The [storage] extra is required for ParquetDuckDBMarketDataStore. "
            "Install with: pip install indiciumforge-core[storage]"
        ) from exc
    return pa, pq  # type: ignore[name-defined]


def _split_uid(asset_uid: str) -> tuple[str, str, str]:
    """Parse the canonical ``exchange:asset_type:code`` uid into its parts."""
    parts = asset_uid.split(":", 2)
    if len(parts) != 3 or not all(parts):
        raise ValueError(f"invalid asset_uid {asset_uid!r}; expected 'exchange:asset_type:code'")
    return parts[0], parts[1], parts[2]


class ParquetDuckDBMarketDataStore:
    """A ``MarketDataStore`` writing partitioned Parquet and reading via DuckDB."""

    def __init__(self, root: Path) -> None:
        self._root = Path(root)
        self._ohlcv_root = self._root / "ohlcv"
        self._ohlcv_root.mkdir(parents=True, exist_ok=True)

    # -- path helpers ---------------------------------------------------------
    def _asset_dir(self, asset_uid: str) -> Path:
        exchange, asset_type, code = _split_uid(asset_uid)
        return self._ohlcv_root / exchange / asset_type / code

    def _asset_glob(self, asset_uid: str) -> str:
        return str(self._asset_dir(asset_uid) / "**" / "*.parquet")

    # -- write ----------------------------------------------------------------
    def write_ohlcv(
        self, asset_uid: str, frame: pd.DataFrame, *, provenance: ProviderProvenance
    ) -> None:
        if frame.empty:
            return
        if "date" not in frame.columns:
            raise ValueError("OHLCV frame must contain a 'date' column")

        pa, pq = _require_storage_deps()
        exchange, asset_type, code = _split_uid(asset_uid)

        out = frame.copy()
        as_of_str = provenance.as_of.isoformat() if provenance.as_of else ""
        out["p_provider"] = provenance.provider_id
        out["p_tier"] = provenance.authority_level.value
        out["p_as_of"] = as_of_str
        out["p_captured_at"] = provenance.captured_at
        out["p_warnings"] = json.dumps(list(provenance.warnings), ensure_ascii=False)
        out["p_payload"] = json.dumps(provenance.to_payload(), ensure_ascii=False)

        # Normalize the date column and derive the year partition key.
        dates = pd.to_datetime(out["date"]).dt.date
        out["date"] = pd.Series(dates, index=out.index)
        out["year"] = pd.Series([d.year for d in dates], index=out.index, dtype="int32")

        table = pa.Table.from_pandas(out, preserve_index=False)

        # Write Hive-partitioned Parquet. A uuid in the basename guarantees
        # unique part files across repeated writes (overlapping ranges are
        # de-duplicated at read time via the captured_at window).
        self._asset_dir(asset_uid).mkdir(parents=True, exist_ok=True)
        pq.write_to_dataset(
            table,
            root_path=str(self._asset_dir(asset_uid)),
            partition_cols=["year"],
            basename_template=f"part-{uuid.uuid4().hex}-{{i}}.parquet",
        )

    # -- read helpers ---------------------------------------------------------
    def _read_deduped(
        self,
        asset_uid: str,
        *,
        start: date | None,
        end: date | None,
        as_of: date | None,
    ) -> tuple[pd.DataFrame, Provenance | None]:
        """Return the point-in-time de-duplicated OHLCV frame and its provenance.

        The returned frame is stripped of internal provenance columns; the
        reconstructed domain :class:`Provenance` (or ``None`` when empty) is
        returned alongside.
        """

        asset_dir = self._asset_dir(asset_uid)
        if not asset_dir.exists():
            return pd.DataFrame(columns=list(OHLCV_COLUMNS)), None

        import duckdb

        as_of_sql = as_of.isoformat() if as_of is not None else None
        con = duckdb.connect(database=":memory:")

        # Build the point-in-time + range predicate.
        #
        # Point-in-time correctness follows the point-in-time spec exactly: a row is
        # admissible only when its trade ``date`` and the snapshot's own
        # ``provenance_as_of`` (the last trade date it represents) are both on
        # or before ``as_of``. This prevents look-ahead on the *data* axis. The
        # ``captured_at`` column is intentionally NOT used as a hard filter here:
        # a live cache populated "now" carries a capture timestamp after the
        # trade date, and excluding it would void the cache. ``captured_at`` is
        # still used for de-duplication (latest snapshot wins), see below.
        predicates: list[str] = []
        params: list[Any] = []
        if as_of is not None:
            predicates.append("CAST(date AS DATE) <= ?::DATE")
            params.append(as_of_sql)
            # provenance_as_of guard (empty/NULL means "unknown" -> not limited)
            predicates.append(
                "(p_as_of IS NULL OR p_as_of = '' OR CAST(p_as_of AS DATE) <= ?::DATE)"
            )
            params.append(as_of_sql)
        if start is not None:
            predicates.append("CAST(date AS DATE) >= ?::DATE")
            params.append(start.isoformat())
        if end is not None:
            predicates.append("CAST(date AS DATE) <= ?::DATE")
            params.append(end.isoformat())

        where = "WHERE " + " AND ".join(predicates) if predicates else ""

        sql = f"""
            WITH raw AS (
                SELECT *,
                       ROW_NUMBER() OVER (
                           PARTITION BY date ORDER BY p_captured_at DESC
                       ) AS _rn
                FROM read_parquet('{self._asset_glob(asset_uid)}')
                {where}
            )
            SELECT * FROM raw WHERE _rn = 1 ORDER BY date
        """
        df = con.execute(sql, params).fetch_df()

        if df.empty:
            return pd.DataFrame(columns=list(OHLCV_COLUMNS)), None

        # Pull the provenance payload from the surviving snapshot.
        payload_raw = df["p_payload"].iloc[0]
        prov = self._provenance_from_payload(payload_raw)

        # Strip internal columns, keeping only user-facing OHLCV (+ extras).
        drop_cols = [c for c in list(df.columns) if c.startswith("p_") or c in ("year", "_rn")]
        df = df.drop(columns=drop_cols).reset_index(drop=True)
        return df, prov

    @staticmethod
    def _provenance_from_payload(payload_raw: str) -> Provenance:
        payload = json.loads(payload_raw)
        as_of = None
        if payload.get("as_of"):
            as_of = date.fromisoformat(payload["as_of"])
        return Provenance(
            provider=payload.get("provider_id", "unknown"),
            tier=payload.get("authority_level", "unknown"),
            as_of=as_of,
            fetched_at=payload.get("captured_at", ""),
            warnings=tuple(payload.get("warnings", [])),
        )

    # -- MarketDataStore API --------------------------------------------------
    def fetch_ohlcv(
        self,
        asset_uid: str,
        *,
        start: date | None = None,
        end: date | None = None,
        as_of: date | None = None,
    ) -> FetchResult:
        frame, prov = self._read_deduped(asset_uid, start=start, end=end, as_of=as_of)
        if prov is None:
            from indiciumforge_core.clock import utc_now_iso

            prov = Provenance(
                provider="market_data_store",
                tier="cache",
                as_of=as_of,
                fetched_at=utc_now_iso(),
                warnings=("cache miss / empty coverage",),
            )
        return frame, prov

    def fetch_ohlcv_batch(
        self,
        asset_uids: list[str],
        *,
        start: date | None = None,
        end: date | None = None,
        as_of: date | None = None,
    ) -> dict[str, FetchResult]:
        return {
            uid: self.fetch_ohlcv(uid, start=start, end=end, as_of=as_of)
            for uid in asset_uids
        }

    def fetch_panel(
        self,
        asset_uids: list[str],
        *,
        start: date,
        end: date,
        as_of: date | None = None,
    ) -> pd.DataFrame:
        frames: list[pd.DataFrame] = []
        for uid in asset_uids:
            frame, _ = self._read_deduped(uid, start=start, end=end, as_of=as_of)
            if frame.empty:
                continue
            frame = frame.copy()
            frame.insert(0, "asset_uid", uid)
            frames.append(frame)
        if not frames:
            return pd.DataFrame(columns=["asset_uid", *OHLCV_COLUMNS])
        return pd.concat(frames, ignore_index=True).sort_values(["date", "asset_uid"])

    def has_coverage(self, asset_uid: str, *, start: date, end: date) -> bool:
        asset_dir = self._asset_dir(asset_uid)
        if not asset_dir.exists():
            return False
        import duckdb

        con = duckdb.connect(database=":memory:")
        sql = f"""
            SELECT COUNT(*) AS n
            FROM read_parquet('{self._asset_glob(asset_uid)}')
            WHERE CAST(date AS DATE) >= ?::DATE
              AND CAST(date AS DATE) <= ?::DATE
        """
        result = con.execute(sql, [start.isoformat(), end.isoformat()]).fetchone()
        return bool(result and result[0] > 0)


# Mark as a structural subtype of the port (no runtime cost, aids type checkers).
MarketDataStore.register(ParquetDuckDBMarketDataStore)
