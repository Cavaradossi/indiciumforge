from __future__ import annotations

from typing import Protocol

from indiciumforge_core.providers.capabilities import ProviderAuthorityLevel, ProviderCapability
from indiciumforge_core.providers.query import DataQuery
from indiciumforge_core.providers.result import ProviderResult


class DataProviderPortV2(Protocol):
    provider_id: str
    authority_level: ProviderAuthorityLevel
    capabilities: tuple[ProviderCapability, ...]

    def supports_query(self, query: DataQuery) -> bool: ...

    def fetch(self, query: DataQuery) -> ProviderResult: ...
