from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path
from typing import Any

from lucerna_core.artifacts.paths import post_close_review_dir, preopen_review_dir
from lucerna_core.domain.models import AssetID
from lucerna_core.factors.pack import load_factor_pack
from lucerna_core.factors.scan import FactorScanRunner
from lucerna_core.factors.universe import load_assets_from_fixture_list
from lucerna_core.labels.market_gate import REVIEW_COLUMNS
from lucerna_core.providers.local_fixture import LocalFixtureProvider
from lucerna_core.providers.registry import ProviderRegistry
from lucerna_core.recipes.models import RecipeStageContext, StageRunResult
from lucerna_core.workflow.handoff import HandoffArtifactKind

POST_CLOSE_REVIEW_STATE_SCHEMA = "lucerna.post_close_review_state.v1"
PREOPEN_REVIEW_STATE_SCHEMA = "lucerna.preopen_review_state.v1"
CANDIDATE_POOL_RAW_SCHEMA = "lucerna.candidate_pool_raw.v1"


class FakeAshareRecipeExtension:
    """Synthetic A-share recipe extension for OSS contract tests."""

    extension_id = "fake_ashare_recipe"
    recipe_ids = ("lucerna.recipe.ashare_daily_research.v1",)

    def __init__(
        self,
        *,
        ohlcv_fixture_root: Path | str | None = None,
        factor_detectors_config: Path | str | None = None,
        asset_fixture_list: Path | str | None = None,
        post_close_review_fixture: Path | str | None = None,
        preopen_review_fixture: Path | str | None = None,
    ) -> None:
        self._ohlcv_fixture_root = Path(ohlcv_fixture_root) if ohlcv_fixture_root else None
        self._factor_detectors_config = (
            Path(factor_detectors_config) if factor_detectors_config else None
        )
        self._asset_fixture_list = Path(asset_fixture_list) if asset_fixture_list else None
        self._post_close_review_fixture = (
            Path(post_close_review_fixture) if post_close_review_fixture else None
        )
        self._preopen_review_fixture = (
            Path(preopen_review_fixture) if preopen_review_fixture else None
        )

    def supports_stage(self, recipe_id: str, stage_id: str) -> bool:
        return recipe_id in self.recipe_ids and stage_id in (
            "discovery_post_close",
            "handoff_preopen",
        )

    def execute_stage(self, context: RecipeStageContext) -> StageRunResult:
        if context.stage.stage_id == "discovery_post_close":
            return self._run_post_close(context)
        if context.stage.stage_id == "handoff_preopen":
            return self._run_preopen(context)
        raise ValueError(f"unsupported stage: {context.stage.stage_id}")

    def _run_post_close(self, context: RecipeStageContext) -> StageRunResult:
        stage_dir = post_close_review_dir(context.artifact_root, context.trade_date)
        stage_dir.mkdir(parents=True, exist_ok=True)
        warnings: list[str] = []
        artifacts: list[str] = []

        pool_path = stage_dir / "candidate_pool_raw.json"
        signals = self._scan_signals(context)
        pool_payload = self._build_candidate_pool(context.trade_date, signals)
        pool_path.write_text(
            json.dumps(pool_payload, ensure_ascii=False, indent=2),
            encoding="utf-8-sig",
        )
        artifacts.append("candidate_pool_raw.json")

        review_path = stage_dir / "buy_point_review_internal.csv"
        if self._post_close_review_fixture and self._post_close_review_fixture.is_file():
            shutil.copy2(self._post_close_review_fixture, review_path)
            provenance_source = "synthetic_fixture"
            fixture_name = self._post_close_review_fixture.name
        else:
            self._write_review_from_signals(review_path, signals)
            provenance_source = "fake_recipe_extension"
            fixture_name = "generated"
        artifacts.append("buy_point_review_internal.csv")

        state_path = stage_dir / "post_close_review_state.json"
        state_path.write_text(
            json.dumps(
                {
                    "schema": POST_CLOSE_REVIEW_STATE_SCHEMA,
                    "trade_date": context.trade_date.isoformat(),
                    "stage": "post_close",
                    "paths": {
                        "buy_point_review_internal": review_path.name,
                        "candidate_pool_raw": pool_path.name,
                    },
                    "provenance": {
                        "source": provenance_source,
                        "extension_id": self.extension_id,
                        "fixture": fixture_name,
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8-sig",
        )
        artifacts.append("post_close_review_state.json")

        return StageRunResult(
            stage_id=context.stage.stage_id,
            stage_dir=stage_dir,
            artifacts=tuple(artifacts),
            warnings=tuple(warnings),
            audit_ok=True,
            extra={"signal_count": len(signals)},
        )

    def _run_preopen(self, context: RecipeStageContext) -> StageRunResult:
        stage_dir = preopen_review_dir(context.artifact_root, context.trade_date)
        stage_dir.mkdir(parents=True, exist_ok=True)
        warnings: list[str] = []
        artifacts: list[str] = []

        pool_key = f"discovery_post_close:{HandoffArtifactKind.CANDIDATE_POOL_RAW.value}"
        pool_path = context.inputs.get(pool_key)
        if pool_path is None or not pool_path.is_file():
            warnings.append("missing post_close candidate_pool_raw handoff; continuing with stub")
        else:
            artifacts.append("candidate_pool_raw.json")

        review_path = stage_dir / "buy_point_review_internal.csv"
        if self._preopen_review_fixture and self._preopen_review_fixture.is_file():
            shutil.copy2(self._preopen_review_fixture, review_path)
            provenance_source = "synthetic_fixture"
            fixture_name = self._preopen_review_fixture.name
        elif pool_path is not None and pool_path.is_file():
            shutil.copy2(pool_path.parent / "buy_point_review_internal.csv", review_path)
            provenance_source = "post_close_handoff"
            fixture_name = "post_close_review"
        else:
            raise FileNotFoundError(
                "preopen review requires preopen_review_fixture or post_close handoff"
            )

        artifacts.append("buy_point_review_internal.csv")

        state_path = stage_dir / "preopen_review_state.json"
        state_path.write_text(
            json.dumps(
                {
                    "schema": PREOPEN_REVIEW_STATE_SCHEMA,
                    "trade_date": context.trade_date.isoformat(),
                    "stage": "preopen",
                    "paths": {"buy_point_review_internal": review_path.name},
                    "provenance": {
                        "source": provenance_source,
                        "extension_id": self.extension_id,
                        "fixture": fixture_name,
                        "market_context": "stub_empty",
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8-sig",
        )
        artifacts.append("preopen_review_state.json")

        return StageRunResult(
            stage_id=context.stage.stage_id,
            stage_dir=stage_dir,
            artifacts=tuple(artifacts),
            warnings=tuple(warnings),
            audit_ok=True,
        )

    def _scan_signals(self, context: RecipeStageContext) -> list[dict[str, Any]]:
        if self._ohlcv_fixture_root is None or self._factor_detectors_config is None:
            return []
        assets: tuple[AssetID, ...] = ()
        if self._asset_fixture_list is not None:
            assets = tuple(load_assets_from_fixture_list(self._asset_fixture_list))
        if not assets:
            return []

        loaded = load_factor_pack(detectors_config=self._factor_detectors_config)
        provider_registry = ProviderRegistry(
            [LocalFixtureProvider(self._ohlcv_fixture_root)]
        )
        runner = FactorScanRunner(provider_registry, loaded.registry)
        result = runner.scan(list(assets), context.trade_date)
        return [
            {
                "code": signal.asset.code,
                "factor": signal.factor,
                "score": signal.score,
                "matched": signal.matched,
            }
            for signal in result.signals
        ]

    def _build_candidate_pool(
        self,
        trade_date: date,
        signals: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return {
            "schema": CANDIDATE_POOL_RAW_SCHEMA,
            "trade_date": trade_date.isoformat(),
            "candidates": signals,
            "provenance": {
                "source": "fake_recipe_extension",
                "extension_id": self.extension_id,
            },
        }

    def _write_review_from_signals(
        self,
        review_path: Path,
        signals: list[dict[str, Any]],
    ) -> None:
        columns = list(REVIEW_COLUMNS.values())
        lines = [",".join(columns)]
        for signal in signals:
            row = [
                "A-可重点复核",
                signal.get("code", "000001"),
                "fake候选",
                "强方向",
                "强方向",
                "",
                "波段观察",
                "主线扩散",
                "暂无",
                "0项",
                "未见明显风险",
            ]
            lines.append(",".join(row))
        review_path.write_text("\n".join(lines) + "\n", encoding="utf-8-sig")
