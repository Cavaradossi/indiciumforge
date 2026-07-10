from __future__ import annotations

from enum import Enum

HANDOFF_ARTIFACT_SCHEMA = "indiciumforge.handoff_artifact.v1"


class HandoffArtifactKind(str, Enum):
    THEME_STATE_RANKING = "theme_state_ranking"
    FACTOR_SCAN_JSON = "factor_scan_json"
    CANDIDATE_POOL_RAW = "candidate_pool_raw"
    BUY_POINT_REVIEW_INTERNAL = "buy_point_review_internal"
    BUY_POINT_REVIEW_PUBLIC = "buy_point_review_public"
    MARKET_GATE_STRICT = "market_gate_strict"
    MARKET_GATE_SUMMARY = "market_gate_summary"


HANDOFF_ARTIFACT_FILE_HINTS: dict[HandoffArtifactKind, str] = {
    HandoffArtifactKind.THEME_STATE_RANKING: "theme_state_ranking.csv",
    HandoffArtifactKind.FACTOR_SCAN_JSON: "factor_scan_{date}.json",
    HandoffArtifactKind.CANDIDATE_POOL_RAW: "candidate_pool_raw.json",
    HandoffArtifactKind.BUY_POINT_REVIEW_INTERNAL: "buy_point_review_internal.csv",
    HandoffArtifactKind.BUY_POINT_REVIEW_PUBLIC: "buy_point_review.csv",
    HandoffArtifactKind.MARKET_GATE_STRICT: "market_gated_candidates.csv",
    HandoffArtifactKind.MARKET_GATE_SUMMARY: "market_gate_summary.json",
}
