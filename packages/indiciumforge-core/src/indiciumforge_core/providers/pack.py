from __future__ import annotations

from dataclasses import dataclass

from indiciumforge_core.providers.contracts_v2 import DataProviderPortV2

PROVIDER_PACK_SCHEMA = "indiciumforge.provider_pack.v1"


@dataclass(frozen=True)
class LoadedProviderPack:
    pack_id: str | None
    version: str | None
    providers: tuple[DataProviderPortV2, ...]
    sources: tuple[str, ...]
