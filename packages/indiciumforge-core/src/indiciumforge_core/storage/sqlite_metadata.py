"""Relational metadata store backed by the stdlib :mod:`sqlite3` (WAL mode).

No third-party dependency — DuckDB/Parquet are only needed for the time-series
data layer (``parquet_duckdb``). This module implements the
``MetadataStore`` port from :mod:`indiciumforge_core.ports.storage`.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date
from pathlib import Path

from indiciumforge_core.ports.storage import (
    FactorMetaRecord,
    ParityReportRecord,
    RunRecord,
    StageRecord,
)

_JSON_COLUMNS_RUN = ("meta",)
_JSON_COLUMNS_STAGE = ("warnings", "extra")
_JSON_COLUMNS_FACTOR = ("meta",)
_JSON_COLUMNS_PARITY = ("summary",)


def _iso(value: date | str | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value.isoformat()
    return value


def _loads(text: str | None) -> dict[str, object]:
    if not text:
        return {}
    return json.loads(text)


def _loads_tuple(text: str | None) -> tuple[str, ...]:
    if not text:
        return ()
    data = json.loads(text)
    return tuple(data) if isinstance(data, list) else ()


class SQLiteMetadataStore:
    """A ``MetadataStore`` implementation using SQLite with WAL journaling."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self._db_path))
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                recipe_id TEXT NOT NULL,
                asset_domain TEXT NOT NULL,
                session_model TEXT NOT NULL,
                cycle_id TEXT NOT NULL,
                trade_date TEXT NOT NULL,
                started_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'ok',
                meta TEXT NOT NULL DEFAULT '{}'
            );
            CREATE TABLE IF NOT EXISTS stages (
                stage_id TEXT NOT NULL,
                run_id TEXT NOT NULL,
                recipe_id TEXT NOT NULL,
                trade_date TEXT NOT NULL,
                status TEXT NOT NULL,
                input_descriptor_hash TEXT NOT NULL,
                output_content_hash TEXT NOT NULL,
                provider_id TEXT,
                warnings TEXT NOT NULL DEFAULT '[]',
                extra TEXT NOT NULL DEFAULT '{}',
                rowid_meta INTEGER PRIMARY KEY AUTOINCREMENT,
                FOREIGN KEY (run_id) REFERENCES runs (run_id)
            );
            CREATE TABLE IF NOT EXISTS factor_metadata (
                factor_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                asset_domain TEXT NOT NULL,
                version TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                meta TEXT NOT NULL DEFAULT '{}'
            );
            CREATE TABLE IF NOT EXISTS parity_reports (
                report_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                dimension TEXT NOT NULL,
                status TEXT NOT NULL,
                summary TEXT NOT NULL DEFAULT '{}',
                generated_at TEXT NOT NULL DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_stages_lookup
                ON stages (recipe_id, stage_id, trade_date, input_descriptor_hash);
            CREATE INDEX IF NOT EXISTS idx_runs_trade_date ON runs (trade_date);
            """
        )
        self._conn.commit()

    # -- runs -----------------------------------------------------------------
    def record_run(self, run: RunRecord) -> None:
        self._conn.execute(
            """
            INSERT INTO runs (
                run_id, recipe_id, asset_domain, session_model, cycle_id,
                trade_date, started_at, status, meta
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (run_id) DO UPDATE SET
                recipe_id=excluded.recipe_id,
                asset_domain=excluded.asset_domain,
                session_model=excluded.session_model,
                cycle_id=excluded.cycle_id,
                trade_date=excluded.trade_date,
                started_at=excluded.started_at,
                status=excluded.status,
                meta=excluded.meta
            """,
            (
                run.run_id,
                run.recipe_id,
                run.asset_domain,
                run.session_model,
                run.cycle_id,
                run.trade_date,
                run.started_at,
                run.status,
                json.dumps(run.meta, sort_keys=True),
            ),
        )
        self._conn.commit()

    def get_run(self, run_id: str) -> RunRecord | None:
        row = self._conn.execute(
            "SELECT * FROM runs WHERE run_id = ?", (run_id,)
        ).fetchone()
        return self._row_to_run(row) if row is not None else None

    def list_runs(
        self,
        *,
        trade_date: date | str | None = None,
        recipe_id: str | None = None,
    ) -> list[RunRecord]:
        clauses: list[str] = []
        params: list[object] = []
        if trade_date is not None:
            clauses.append("trade_date = ?")
            params.append(_iso(trade_date))
        if recipe_id is not None:
            clauses.append("recipe_id = ?")
            params.append(recipe_id)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self._conn.execute(
            f"SELECT * FROM runs {where} ORDER BY trade_date, run_id", params
        ).fetchall()
        return [self._row_to_run(r) for r in rows]

    def _row_to_run(self, row: sqlite3.Row) -> RunRecord:
        return RunRecord(
            run_id=row["run_id"],
            recipe_id=row["recipe_id"],
            asset_domain=row["asset_domain"],
            session_model=row["session_model"],
            cycle_id=row["cycle_id"],
            trade_date=row["trade_date"],
            started_at=row["started_at"],
            status=row["status"],
            meta=_loads(row["meta"]),
        )

    # -- stages ----------------------------------------------------------------
    def record_stage(self, stage: StageRecord) -> None:
        self._conn.execute(
            """
            INSERT INTO stages (
                stage_id, run_id, recipe_id, trade_date, status,
                input_descriptor_hash, output_content_hash, provider_id,
                warnings, extra
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                stage.stage_id,
                stage.run_id,
                stage.recipe_id,
                stage.trade_date,
                stage.status,
                stage.input_descriptor_hash,
                stage.output_content_hash,
                stage.provider_id,
                json.dumps(list(stage.warnings)),
                json.dumps(stage.extra, sort_keys=True),
            ),
        )
        self._conn.commit()

    def find_stage_by_input_hash(
        self,
        *,
        recipe_id: str,
        stage_id: str,
        trade_date: str,
        input_descriptor_hash: str,
    ) -> StageRecord | None:
        row = self._conn.execute(
            """
            SELECT * FROM stages
            WHERE recipe_id = ? AND stage_id = ? AND trade_date = ?
              AND input_descriptor_hash = ?
            ORDER BY rowid_meta DESC
            LIMIT 1
            """,
            (recipe_id, stage_id, trade_date, input_descriptor_hash),
        ).fetchone()
        return self._row_to_stage(row) if row is not None else None

    def _row_to_stage(self, row: sqlite3.Row) -> StageRecord:
        return StageRecord(
            stage_id=row["stage_id"],
            run_id=row["run_id"],
            recipe_id=row["recipe_id"],
            trade_date=row["trade_date"],
            status=row["status"],
            input_descriptor_hash=row["input_descriptor_hash"],
            output_content_hash=row["output_content_hash"],
            provider_id=row["provider_id"],
            warnings=_loads_tuple(row["warnings"]),
            extra=_loads(row["extra"]),
        )

    # -- factor metadata -------------------------------------------------------
    def record_factor_metadata(self, rec: FactorMetaRecord) -> None:
        self._conn.execute(
            """
            INSERT INTO factor_metadata (
                factor_id, name, asset_domain, version, description, meta
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT (factor_id) DO UPDATE SET
                name=excluded.name,
                asset_domain=excluded.asset_domain,
                version=excluded.version,
                description=excluded.description,
                meta=excluded.meta
            """,
            (
                rec.factor_id,
                rec.name,
                rec.asset_domain,
                rec.version,
                rec.description,
                json.dumps(rec.meta, sort_keys=True),
            ),
        )
        self._conn.commit()

    def get_factor_metadata(self, factor_id: str) -> FactorMetaRecord | None:
        row = self._conn.execute(
            "SELECT * FROM factor_metadata WHERE factor_id = ?", (factor_id,)
        ).fetchone()
        return self._row_to_factor(row) if row is not None else None

    def _row_to_factor(self, row: sqlite3.Row) -> FactorMetaRecord:
        return FactorMetaRecord(
            factor_id=row["factor_id"],
            name=row["name"],
            asset_domain=row["asset_domain"],
            version=row["version"],
            description=row["description"],
            meta=_loads(row["meta"]),
        )

    def record_parity_report(self, rec: ParityReportRecord) -> None:
        self._conn.execute(
            """
            INSERT INTO parity_reports (
                report_id, run_id, dimension, status, summary, generated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT (report_id) DO UPDATE SET
                run_id=excluded.run_id,
                dimension=excluded.dimension,
                status=excluded.status,
                summary=excluded.summary,
                generated_at=excluded.generated_at
            """,
            (
                rec.report_id,
                rec.run_id,
                rec.dimension,
                rec.status,
                json.dumps(rec.summary, sort_keys=True),
                rec.generated_at,
            ),
        )
        self._conn.commit()

    def get_parity_report(self, report_id: str) -> ParityReportRecord | None:
        row = self._conn.execute(
            "SELECT * FROM parity_reports WHERE report_id = ?", (report_id,)
        ).fetchone()
        return self._row_to_parity(row) if row is not None else None

    def _row_to_parity(self, row: sqlite3.Row) -> ParityReportRecord:
        return ParityReportRecord(
            report_id=row["report_id"],
            run_id=row["run_id"],
            dimension=row["dimension"],
            status=row["status"],
            summary=_loads(row["summary"]),
            generated_at=row["generated_at"],
        )

    # -- generic key/value meta ------------------------------------------------
    def set_meta(self, key: str, value: str) -> None:
        self._conn.execute(
            "INSERT INTO meta (key, value) VALUES (?, ?) "
            "ON CONFLICT (key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
        self._conn.commit()

    def get_meta(self, key: str) -> str | None:
        row = self._conn.execute(
            "SELECT value FROM meta WHERE key = ?", (key,)
        ).fetchone()
        return row["value"] if row is not None else None

    def close(self) -> None:
        self._conn.close()
