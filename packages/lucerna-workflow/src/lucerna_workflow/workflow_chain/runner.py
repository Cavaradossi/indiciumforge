from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from lucerna_core.artifacts.manifest import (
    validate_daily_review_stage,
    validate_factor_scan_stage,
    validate_market_gate_stage,
)
from lucerna_core.artifacts.paths import (
    daily_review_dir,
    factor_scan_dir,
    market_gate_stage_dir,
    post_close_review_dir,
    preopen_review_dir,
    workflow_chain_summary_path,
)
from lucerna_core.recipes.models import RecipeStageContext, StageRunResult
from lucerna_core.recipes.pack import LoadedRecipeExtensionPack, load_recipe_extension_pack
from lucerna_core.recipes.runner import RecipeRunner
from lucerna_core.workflow.model import (
    DEFAULT_ASHARE_RECIPE_ID,
    AssetDomain,
    SessionModel,
    WorkflowRecipe,
    WorkflowSessionMetadata,
    ashare_cycle_id,
)
from lucerna_core.workflow.recipe_schema import load_workflow_recipe

from lucerna_workflow.factor_scan.runner import FactorScanStageConfig, run_factor_scan_stage
from lucerna_workflow.market_awareness.runner import run_daily_review_skeleton
from lucerna_workflow.market_gate.runner import run_market_gate
from lucerna_workflow.workflow_chain.skeleton import seed_post_close_review, seed_preopen_review

WORKFLOW_CHAIN_SUMMARY_SCHEMA = "lucerna.workflow_chain_summary.v3"
WORKFLOW_CHAIN_SUMMARY_SCHEMA_V4 = "lucerna.workflow_chain_summary.v4"


@dataclass(frozen=True)
class WorkflowChainRecipeConfig:
    recipe_path: Path
    recipe_extension_pack: Path | None = None
    daily_review_fixture: Path | None = None
    factor_scan_config: FactorScanStageConfig | None = None


@dataclass(frozen=True)
class WorkflowChainResult:
    trade_date: date
    daily_review_stage_dir: Path
    post_close_stage_dir: Path
    preopen_stage_dir: Path
    market_gate_stage_dir: Path
    summary_path: Path
    workflow_review_source_stage: str
    strict_count: int
    daily_review_audit_ok: bool
    market_gate_audit_ok: bool
    chain_ok: bool
    warnings: tuple[str, ...]
    factor_scan_enabled: bool = False
    factor_scan_stage_dir: Path | None = None
    factor_scan_audit_ok: bool | None = None
    detector_count: int = 0
    signal_count: int = 0
    recipe_id: str | None = None
    recipe_run_summary_path: Path | None = None
    extension_pack_id: str | None = None


def _build_recipe_stage_handlers(
    *,
    daily_review_fixture: Path | None,
    factor_scan_config: FactorScanStageConfig | None,
) -> dict[str, Any]:
    def awareness_daily_review(context: RecipeStageContext) -> StageRunResult:
        fixture = daily_review_fixture or context.options.get("daily_review_fixture")
        if fixture is None or not Path(fixture).is_file():
            raise FileNotFoundError("recipe chain requires --daily-review-fixture")
        result = run_daily_review_skeleton(
            trade_date=context.trade_date,
            artifact_root=context.artifact_root,
            fixture_path=Path(fixture),
        )
        stage_dir = daily_review_dir(context.artifact_root, context.trade_date)
        return StageRunResult(
            stage_id=context.stage.stage_id,
            stage_dir=stage_dir,
            artifacts=("theme_state_ranking.csv", "market_daily_review_state.json"),
            warnings=result.warnings,
            audit_ok=True,
        )

    def evidence_factor_scan(context: RecipeStageContext) -> StageRunResult:
        config = factor_scan_config or context.options.get("factor_scan_config")
        if config is None:
            return StageRunResult(
                stage_id=context.stage.stage_id,
                stage_dir=factor_scan_dir(context.artifact_root, context.trade_date),
                warnings=("factor scan not configured; skipped",),
                empty_result_reason="factor_scan_not_configured",
            )
        result = run_factor_scan_stage(
            trade_date=context.trade_date,
            artifact_root=context.artifact_root,
            config=config,
        )
        scan_json = f"factor_scan_{context.trade_date.strftime('%Y%m%d')}.json"
        return StageRunResult(
            stage_id=context.stage.stage_id,
            stage_dir=result.stage_dir,
            artifacts=(scan_json, "factor_scan_state.json"),
            warnings=result.warnings,
            audit_ok=True,
            extra={
                "detector_count": result.detector_count,
                "signal_count": result.signal_count,
            },
        )

    def gate_market_theme(context: RecipeStageContext) -> StageRunResult:
        result = run_market_gate(
            trade_date=context.trade_date,
            artifact_root=context.artifact_root,
        )
        return StageRunResult(
            stage_id=context.stage.stage_id,
            stage_dir=result.stage_dir,
            artifacts=tuple(result.paths.keys()),
            warnings=tuple(result.warnings),
            audit_ok=True,
        )

    return {
        "awareness_daily_review": awareness_daily_review,
        "evidence_factor_scan": evidence_factor_scan,
        "gate_market_theme": gate_market_theme,
    }


def _write_chain_summary_v4(
    path: Path,
    *,
    trade_date: date,
    recipe: WorkflowRecipe,
    extension_pack: LoadedRecipeExtensionPack | None,
    stage_results: tuple[StageRunResult, ...],
    daily_review_audit_ok: bool,
    market_gate_audit_ok: bool,
    workflow_review_source_stage: str,
    strict_count: int,
    warnings: list[str],
    factor_scan_enabled: bool,
    factor_scan_audit_ok: bool | None,
    detector_count: int,
    signal_count: int,
    recipe_run_summary_path: Path,
) -> None:
    stages: dict[str, Any] = {}
    for result in stage_results:
        folder = result.stage_dir.name
        entry: dict[str, Any] = {
            "stage_id": result.stage_id,
            "dir": str(result.stage_dir),
            "artifacts": list(result.artifacts),
        }
        if result.audit_ok is not None:
            entry["audit_ok"] = result.audit_ok
        if result.empty_result_reason:
            entry["empty_result_reason"] = result.empty_result_reason
        stages[folder] = entry

    provenance: dict[str, Any] = {
        "mode": "workflow_chain_recipe",
        "recipe_path": str(recipe.recipe_id),
        "recipe_run_summary": str(recipe_run_summary_path),
    }
    if extension_pack is not None:
        provenance["extension_pack"] = {
            "pack_id": extension_pack.pack_id,
            "version": extension_pack.version,
            "sources": list(extension_pack.sources),
            "extension_ids": [ext.extension_id for ext in extension_pack.extensions],
        }

    payload: dict[str, Any] = {
        "schema": WORKFLOW_CHAIN_SUMMARY_SCHEMA_V4,
        "trade_date": trade_date.isoformat(),
        "workflow_session": WorkflowSessionMetadata(
            recipe_id=recipe.recipe_id,
            asset_domain=recipe.asset_domain,
            session_model=recipe.session_model,
            cycle_id=ashare_cycle_id(trade_date),
        ).to_payload(),
        "provenance": provenance,
        "stages": stages,
        "workflow_review_source_stage": workflow_review_source_stage,
        "strict_count": strict_count,
        "factor_scan_enabled": factor_scan_enabled,
        "factor_scan_audit_ok": factor_scan_audit_ok,
        "detector_count": detector_count,
        "signal_count": signal_count,
        "chain_ok": daily_review_audit_ok and market_gate_audit_ok,
        "warnings": warnings,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8-sig")


def run_workflow_chain_recipe(
    *,
    trade_date: date,
    artifact_root: Path,
    config: WorkflowChainRecipeConfig,
) -> WorkflowChainResult:
    if not config.recipe_path.is_file():
        raise FileNotFoundError(f"missing recipe: {config.recipe_path}")

    recipe = load_workflow_recipe(config.recipe_path)
    extension_pack: LoadedRecipeExtensionPack | None = None
    extensions = ()
    if config.recipe_extension_pack is not None:
        extension_pack = load_recipe_extension_pack(pack_config=config.recipe_extension_pack)
        extensions = extension_pack.extensions

    options: dict[str, Any] = {}
    if config.daily_review_fixture is not None:
        options["daily_review_fixture"] = config.daily_review_fixture
    if config.factor_scan_config is not None:
        options["factor_scan_config"] = config.factor_scan_config

    runner = RecipeRunner(
        extensions=extensions,
        stage_handlers=_build_recipe_stage_handlers(
            daily_review_fixture=config.daily_review_fixture,
            factor_scan_config=config.factor_scan_config,
        ),
    )
    recipe_result = runner.run(
        trade_date=trade_date,
        artifact_root=artifact_root,
        recipe=recipe,
        options=options,
    )

    trade_date_iso = trade_date.isoformat()
    dr_stage_dir = daily_review_dir(artifact_root, trade_date)
    pc_stage_dir = post_close_review_dir(artifact_root, trade_date)
    po_stage_dir = preopen_review_dir(artifact_root, trade_date)
    mg_stage_dir = market_gate_stage_dir(artifact_root, trade_date)
    fs_stage_dir = factor_scan_dir(artifact_root, trade_date)

    daily_manifest = validate_daily_review_stage(
        dr_stage_dir,
        expected_trade_date=trade_date_iso,
    )
    gate_manifest = validate_market_gate_stage(
        mg_stage_dir,
        expected_trade_date=trade_date_iso,
    )

    factor_scan_enabled = config.factor_scan_config is not None
    factor_scan_audit_ok: bool | None = None
    detector_count = 0
    signal_count = 0
    if factor_scan_enabled and fs_stage_dir.is_dir():
        factor_manifest = validate_factor_scan_stage(
            fs_stage_dir,
            expected_trade_date=trade_date_iso,
        )
        factor_scan_audit_ok = factor_manifest.ok
    for result in recipe_result.stage_results:
        if result.stage_id == "evidence_factor_scan":
            detector_count = int(result.extra.get("detector_count", 0))
            signal_count = int(result.extra.get("signal_count", 0))

    daily_review_audit_ok = daily_manifest.ok
    market_gate_audit_ok = gate_manifest.ok
    chain_ok = daily_review_audit_ok and market_gate_audit_ok

    summary_payload = json.loads(
        (mg_stage_dir / "market_gate_summary.json").read_text(encoding="utf-8-sig")
    )
    workflow_review_source_stage = str(summary_payload.get("workflow_review_source_stage", ""))
    strict_count = int(summary_payload.get("strict_count", 0))

    warnings = list(recipe_result.warnings)
    summary_path = workflow_chain_summary_path(artifact_root, trade_date)
    _write_chain_summary_v4(
        summary_path,
        trade_date=trade_date,
        recipe=recipe,
        extension_pack=extension_pack,
        stage_results=recipe_result.stage_results,
        daily_review_audit_ok=daily_review_audit_ok,
        market_gate_audit_ok=market_gate_audit_ok,
        workflow_review_source_stage=workflow_review_source_stage,
        strict_count=strict_count,
        warnings=warnings,
        factor_scan_enabled=factor_scan_enabled,
        factor_scan_audit_ok=factor_scan_audit_ok,
        detector_count=detector_count,
        signal_count=signal_count,
        recipe_run_summary_path=recipe_result.summary_path,
    )

    return WorkflowChainResult(
        trade_date=trade_date,
        daily_review_stage_dir=dr_stage_dir,
        post_close_stage_dir=pc_stage_dir,
        preopen_stage_dir=po_stage_dir,
        market_gate_stage_dir=mg_stage_dir,
        summary_path=summary_path,
        workflow_review_source_stage=workflow_review_source_stage,
        strict_count=strict_count,
        daily_review_audit_ok=daily_review_audit_ok,
        market_gate_audit_ok=market_gate_audit_ok,
        chain_ok=chain_ok,
        warnings=tuple(warnings),
        factor_scan_enabled=factor_scan_enabled,
        factor_scan_stage_dir=fs_stage_dir if factor_scan_enabled else None,
        factor_scan_audit_ok=factor_scan_audit_ok,
        detector_count=detector_count,
        signal_count=signal_count,
        recipe_id=recipe.recipe_id,
        recipe_run_summary_path=recipe_result.summary_path,
        extension_pack_id=extension_pack.pack_id if extension_pack else None,
    )


def _write_chain_summary(
    path: Path,
    *,
    trade_date: date,
    daily_review_stage_dir: Path,
    post_close_stage_dir: Path,
    preopen_stage_dir: Path,
    market_gate_stage_dir: Path,
    daily_review_audit_ok: bool,
    market_gate_audit_ok: bool,
    workflow_review_source_stage: str,
    strict_count: int,
    fixtures: dict[str, str],
    warnings: list[str],
    factor_scan_enabled: bool,
    factor_scan_stage_dir: Path | None,
    factor_scan_audit_ok: bool | None,
    detector_count: int,
    signal_count: int,
) -> None:
    stages: dict[str, Any] = {
        "daily_review": {
            "dir": str(daily_review_stage_dir),
            "audit_ok": daily_review_audit_ok,
        },
        "post_close": {"dir": str(post_close_stage_dir)},
        "preopen": {"dir": str(preopen_stage_dir)},
        "market_gate": {
            "dir": str(market_gate_stage_dir),
            "audit_ok": market_gate_audit_ok,
        },
    }
    if factor_scan_enabled and factor_scan_stage_dir is not None:
        stages["factor_scan"] = {
            "dir": str(factor_scan_stage_dir),
            "audit_ok": factor_scan_audit_ok,
        }

    payload: dict[str, Any] = {
        "schema": WORKFLOW_CHAIN_SUMMARY_SCHEMA,
        "trade_date": trade_date.isoformat(),
        "workflow_session": WorkflowSessionMetadata(
            recipe_id=DEFAULT_ASHARE_RECIPE_ID,
            asset_domain=AssetDomain.CHINA_A_SHARE,
            session_model=SessionModel.CALENDAR_DAY_CYCLE,
            cycle_id=ashare_cycle_id(trade_date),
        ).to_payload(),
        "provenance": {"mode": "workflow_chain_skeleton", "fixtures": fixtures},
        "stages": stages,
        "workflow_review_source_stage": workflow_review_source_stage,
        "strict_count": strict_count,
        "factor_scan_enabled": factor_scan_enabled,
        "factor_scan_audit_ok": factor_scan_audit_ok,
        "detector_count": detector_count,
        "signal_count": signal_count,
        "chain_ok": daily_review_audit_ok and market_gate_audit_ok,
        "warnings": warnings,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8-sig")


def run_workflow_chain_skeleton(
    *,
    trade_date: date,
    artifact_root: Path,
    daily_review_fixture: Path,
    post_close_review_fixture: Path,
    preopen_review_fixture: Path,
    factor_scan_config: FactorScanStageConfig | None = None,
) -> WorkflowChainResult:
    if not daily_review_fixture.is_file():
        raise FileNotFoundError(f"missing daily-review fixture: {daily_review_fixture}")
    if not post_close_review_fixture.is_file():
        raise FileNotFoundError(f"missing post-close review fixture: {post_close_review_fixture}")
    if not preopen_review_fixture.is_file():
        raise FileNotFoundError(f"missing preopen review fixture: {preopen_review_fixture}")

    warnings: list[str] = []
    trade_date_iso = trade_date.isoformat()

    daily_result = run_daily_review_skeleton(
        trade_date=trade_date,
        artifact_root=artifact_root,
        fixture_path=daily_review_fixture,
    )
    warnings.extend(daily_result.warnings)

    factor_scan_enabled = factor_scan_config is not None
    factor_scan_stage_dir: Path | None = None
    factor_scan_audit_ok: bool | None = None
    detector_count = 0
    signal_count = 0

    if factor_scan_config is not None:
        factor_result = run_factor_scan_stage(
            trade_date=trade_date,
            artifact_root=artifact_root,
            config=factor_scan_config,
        )
        factor_scan_stage_dir = factor_result.stage_dir
        detector_count = factor_result.detector_count
        signal_count = factor_result.signal_count
        warnings.extend(factor_result.warnings)

    seed_post_close_review(artifact_root, trade_date, post_close_review_fixture)
    seed_preopen_review(artifact_root, trade_date, preopen_review_fixture)

    gate_result = run_market_gate(trade_date=trade_date, artifact_root=artifact_root)
    warnings.extend(gate_result.warnings)

    dr_stage_dir = daily_review_dir(artifact_root, trade_date)
    pc_stage_dir = post_close_review_dir(artifact_root, trade_date)
    po_stage_dir = preopen_review_dir(artifact_root, trade_date)
    mg_stage_dir = market_gate_stage_dir(artifact_root, trade_date)

    daily_manifest = validate_daily_review_stage(
        dr_stage_dir,
        expected_trade_date=trade_date_iso,
    )
    gate_manifest = validate_market_gate_stage(
        mg_stage_dir,
        expected_trade_date=trade_date_iso,
    )

    if factor_scan_enabled and factor_scan_stage_dir is not None:
        factor_manifest = validate_factor_scan_stage(
            factor_scan_stage_dir,
            expected_trade_date=trade_date_iso,
        )
        factor_scan_audit_ok = factor_manifest.ok

    daily_review_audit_ok = daily_manifest.ok
    market_gate_audit_ok = gate_manifest.ok
    chain_ok = daily_review_audit_ok and market_gate_audit_ok

    summary_payload = json.loads(
        (mg_stage_dir / "market_gate_summary.json").read_text(encoding="utf-8-sig")
    )
    workflow_review_source_stage = str(summary_payload.get("workflow_review_source_stage", ""))
    strict_count = int(summary_payload.get("strict_count", 0))

    fixtures = {
        "daily_review": str(daily_review_fixture),
        "post_close_review": str(post_close_review_fixture),
        "preopen_review": str(preopen_review_fixture),
    }
    if factor_scan_config is not None:
        if factor_scan_config.pack_config is not None:
            fixtures["factor_pack"] = str(factor_scan_config.pack_config)
        if factor_scan_config.detectors_config is not None:
            fixtures["factor_detectors"] = str(factor_scan_config.detectors_config)
        if factor_scan_config.asset_fixture_list is not None:
            fixtures["factor_assets"] = str(factor_scan_config.asset_fixture_list)

    summary_path = workflow_chain_summary_path(artifact_root, trade_date)
    _write_chain_summary(
        summary_path,
        trade_date=trade_date,
        daily_review_stage_dir=dr_stage_dir,
        post_close_stage_dir=pc_stage_dir,
        preopen_stage_dir=po_stage_dir,
        market_gate_stage_dir=mg_stage_dir,
        daily_review_audit_ok=daily_review_audit_ok,
        market_gate_audit_ok=market_gate_audit_ok,
        workflow_review_source_stage=workflow_review_source_stage,
        strict_count=strict_count,
        fixtures=fixtures,
        warnings=warnings,
        factor_scan_enabled=factor_scan_enabled,
        factor_scan_stage_dir=factor_scan_stage_dir,
        factor_scan_audit_ok=factor_scan_audit_ok,
        detector_count=detector_count,
        signal_count=signal_count,
    )

    return WorkflowChainResult(
        trade_date=trade_date,
        daily_review_stage_dir=dr_stage_dir,
        post_close_stage_dir=pc_stage_dir,
        preopen_stage_dir=po_stage_dir,
        market_gate_stage_dir=mg_stage_dir,
        summary_path=summary_path,
        workflow_review_source_stage=workflow_review_source_stage,
        strict_count=strict_count,
        daily_review_audit_ok=daily_review_audit_ok,
        market_gate_audit_ok=market_gate_audit_ok,
        chain_ok=chain_ok,
        warnings=tuple(warnings),
        factor_scan_enabled=factor_scan_enabled,
        factor_scan_stage_dir=factor_scan_stage_dir,
        factor_scan_audit_ok=factor_scan_audit_ok,
        detector_count=detector_count,
        signal_count=signal_count,
    )
