from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from indiciumforge_core.domain.models import AssetID, AssetType, Exchange
from indiciumforge_core.factors.loading import DetectorLoadError


def _parse_asset_entry(entry: dict[str, Any]) -> AssetID:
    code = entry.get("code")
    if not code:
        raise DetectorLoadError("asset entry requires code")
    exchange_raw = str(entry.get("exchange", Exchange.SSE.value))
    asset_type_raw = str(entry.get("asset_type", AssetType.STOCK.value))
    try:
        exchange = Exchange(exchange_raw)
    except ValueError as exc:
        raise DetectorLoadError(f"invalid exchange: {exchange_raw}") from exc
    try:
        asset_type = AssetType(asset_type_raw)
    except ValueError as exc:
        raise DetectorLoadError(f"invalid asset_type: {asset_type_raw}") from exc
    return AssetID(str(code), exchange, asset_type)


def load_assets_from_fixture_list(path: Path) -> list[AssetID]:
    if not path.is_file():
        raise DetectorLoadError(f"asset fixture list not found: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise DetectorLoadError("asset fixture list root must be a mapping")
    entries = payload.get("assets")
    if not isinstance(entries, list) or not entries:
        raise DetectorLoadError("asset fixture list requires non-empty assets list")
    assets: list[AssetID] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise DetectorLoadError("each asset entry must be a mapping")
        assets.append(_parse_asset_entry(entry))
    return assets


def parse_asset_codes(
    codes: str,
    *,
    exchange: Exchange = Exchange.SSE,
    asset_type: AssetType = AssetType.STOCK,
) -> list[AssetID]:
    parsed: list[AssetID] = []
    for raw in codes.split(","):
        code = raw.strip()
        if code:
            parsed.append(AssetID(code, exchange, asset_type))
    if not parsed:
        raise DetectorLoadError("codes must contain at least one asset code")
    return parsed
