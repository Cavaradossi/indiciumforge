from __future__ import annotations

from datetime import date
from pathlib import Path

from indiciumforge_core.ports.storage import (
    FactorMetaRecord,
    ParityReportRecord,
    RunRecord,
    StageRecord,
)
from indiciumforge_core.storage import SQLiteMetadataStore


def _new_store(tmp_path: Path) -> SQLiteMetadataStore:
    return SQLiteMetadataStore(tmp_path / "meta.db")


def test_run_round_trip_preserves_meta(tmp_path: Path) -> None:
    store = _new_store(tmp_path)
    rec = RunRecord(
        run_id="r1",
        recipe_id="recipe_a",
        asset_domain="china_a_share",
        session_model="v1",
        cycle_id="ashare:2026-01-02",
        trade_date="2026-01-02",
        started_at="2026-01-02T09:00:00+00:00",
        status="ok",
        meta={"note": "smoke", "n": 3},
    )
    store.record_run(rec)
    got = store.get_run("r1")
    assert got is not None
    assert got.run_id == "r1"
    assert got.recipe_id == "recipe_a"
    assert got.meta == {"note": "smoke", "n": 3}
    assert store.get_run("missing") is None


def test_list_runs_filters(tmp_path: Path) -> None:
    store = _new_store(tmp_path)
    store.record_run(
        RunRecord(
            run_id="r1",
            recipe_id="recipe_a",
            asset_domain="china_a_share",
            session_model="v1",
            cycle_id="c1",
            trade_date="2026-01-02",
            started_at="t",
        )
    )
    store.record_run(
        RunRecord(
            run_id="r2",
            recipe_id="recipe_b",
            asset_domain="china_a_share",
            session_model="v1",
            cycle_id="c1",
            trade_date="2026-01-02",
            started_at="t",
        )
    )
    store.record_run(
        RunRecord(
            run_id="r3",
            recipe_id="recipe_a",
            asset_domain="china_a_share",
            session_model="v1",
            cycle_id="c1",
            trade_date="2026-01-03",
            started_at="t",
        )
    )

    assert len(store.list_runs(trade_date=date(2026, 1, 2))) == 2
    assert len(store.list_runs(recipe_id="recipe_a")) == 2
    assert len(store.list_runs(trade_date=date(2026, 1, 2), recipe_id="recipe_a")) == 1


def test_record_run_is_idempotent_upsert(tmp_path: Path) -> None:
    store = _new_store(tmp_path)
    store.record_run(
        RunRecord(
            run_id="r1",
            recipe_id="recipe_a",
            asset_domain="china_a_share",
            session_model="v1",
            cycle_id="c1",
            trade_date="2026-01-02",
            started_at="t",
            status="ok",
        )
    )
    store.record_run(
        RunRecord(
            run_id="r1",
            recipe_id="recipe_a",
            asset_domain="china_a_share",
            session_model="v1",
            cycle_id="c1",
            trade_date="2026-01-02",
            started_at="t",
            status="failed",
        )
    )
    assert store.get_run("r1").status == "failed"


def test_find_stage_by_input_hash_returns_latest(tmp_path: Path) -> None:
    store = _new_store(tmp_path)
    # Parent runs must exist (stages.run_id -> runs.run_id FK).
    store.record_run(
        RunRecord(
            run_id="r1",
            recipe_id="recipe_a",
            asset_domain="china_a_share",
            session_model="v1",
            cycle_id="c1",
            trade_date="2026-01-02",
            started_at="t",
        )
    )
    store.record_run(
        RunRecord(
            run_id="r2",
            recipe_id="recipe_a",
            asset_domain="china_a_share",
            session_model="v1",
            cycle_id="c1",
            trade_date="2026-01-02",
            started_at="t",
        )
    )
    common = dict(
        recipe_id="recipe_a",
        stage_id="fetch",
        trade_date="2026-01-02",
        input_descriptor_hash="h123",
    )
    store.record_stage(
        StageRecord(output_content_hash="old", status="ok", **common, run_id="r1")  # type: ignore[arg-type]
    )
    store.record_stage(
        StageRecord(output_content_hash="new", status="ok", **common, run_id="r2")  # type: ignore[arg-type]
    )
    found = store.find_stage_by_input_hash(
        recipe_id="recipe_a",
        stage_id="fetch",
        trade_date="2026-01-02",
        input_descriptor_hash="h123",
    )
    assert found is not None
    # The later-written stage (rowid_meta DESC) wins -> idempotent re-run safety.
    assert found.output_content_hash == "new"
    assert found.run_id == "r2"


def test_find_stage_missing_returns_none(tmp_path: Path) -> None:
    store = _new_store(tmp_path)
    assert (
        store.find_stage_by_input_hash(
            recipe_id="recipe_a",
            stage_id="fetch",
            trade_date="2026-01-02",
            input_descriptor_hash="nope",
        )
        is None
    )


def test_factor_metadata_upsert_and_read(tmp_path: Path) -> None:
    store = _new_store(tmp_path)
    store.record_factor_metadata(
        FactorMetaRecord(
            factor_id="f1",
            name="Volume Breakout",
            asset_domain="china_a_share",
            version="1.0.0",
            description="old",
            meta={"author": "x"},
        )
    )
    # UPSERT must overwrite the description without creating a second row.
    store.record_factor_metadata(
        FactorMetaRecord(
            factor_id="f1",
            name="Volume Breakout",
            asset_domain="china_a_share",
            version="1.0.0",
            description="new description",
            meta={"author": "y"},
        )
    )
    got = store.get_factor_metadata("f1")
    assert got is not None
    assert got.description == "new description"
    assert got.meta == {"author": "y"}
    assert store.get_factor_metadata("missing") is None


def test_parity_report_round_trip(tmp_path: Path) -> None:
    store = _new_store(tmp_path)
    store.record_run(
        RunRecord(
            run_id="r1",
            recipe_id="recipe_a",
            asset_domain="china_a_share",
            session_model="v1",
            cycle_id="c1",
            trade_date="2026-01-02",
            started_at="t",
        )
    )
    store.record_parity_report(
        ParityReportRecord(
            report_id="p1",
            run_id="r1",
            dimension="ohlcv",
            status="pass",
            summary={"delta": 0.0},
            generated_at="2026-01-02T10:00:00+00:00",
        )
    )
    store.record_parity_report(
        ParityReportRecord(
            report_id="p1",
            run_id="r1",
            dimension="ohlcv",
            status="fail",
            summary={"delta": 1.0},
        )
    )
    got = store.get_parity_report("p1")
    assert got is not None
    assert got.status == "fail"
    assert got.summary == {"delta": 1.0}


def test_generic_meta_kv(tmp_path: Path) -> None:
    store = _new_store(tmp_path)
    store.set_meta("schema_version", "25")
    assert store.get_meta("schema_version") == "25"
    assert store.get_meta("missing") is None
