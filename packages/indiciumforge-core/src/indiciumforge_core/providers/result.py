from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Any

import pandas as pd

from indiciumforge_core.clock import utc_now_iso  # noqa: F401  (re-exported for local_fixture_v2)
from indiciumforge_core.providers.capabilities import DataKind, ProviderAuthorityLevel
from indiciumforge_core.workflow.model import AssetDomain, SessionModel


class ProviderFailureStatus(str, Enum):
    OK = "ok"
    EMPTY = "empty"
    STALE = "stale"
    MISSING_CAPABILITY = "missing_capability"
    QUOTA_BLOCKED = "quota_blocked"
    AUTH_MISSING = "auth_missing"
    PROVIDER_ERROR = "provider_error"
    UNSUPPORTED_DOMAIN = "unsupported_domain"


@dataclass(frozen=True)
class ProviderProvenance:
    provider_id: str
    authority_level: ProviderAuthorityLevel
    data_kind: DataKind
    asset_domain: AssetDomain
    captured_at: str
    as_of: date | None = None
    source_timestamp: str | None = None
    cache_hit: bool = False
    cache_policy: str = "none"
    quota_policy: str = "none"
    failure_status: ProviderFailureStatus = ProviderFailureStatus.OK
    session_model: SessionModel | None = None
    checkpoint_id: str | None = None
    cycle_id: str | None = None
    warnings: tuple[str, ...] = ()

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "provider_id": self.provider_id,
            "authority_level": self.authority_level.value,
            "data_kind": self.data_kind.value,
            "asset_domain": self.asset_domain.value,
            "captured_at": self.captured_at,
            "cache_hit": self.cache_hit,
            "cache_policy": self.cache_policy,
            "quota_policy": self.quota_policy,
            "failure_status": self.failure_status.value,
            "warnings": list(self.warnings),
        }
        if self.as_of is not None:
            payload["as_of"] = self.as_of.isoformat()
        if self.source_timestamp is not None:
            payload["source_timestamp"] = self.source_timestamp
        if self.session_model is not None:
            payload["session_model"] = self.session_model.value
        if self.checkpoint_id is not None:
            payload["checkpoint_id"] = self.checkpoint_id
        if self.cycle_id is not None:
            payload["cycle_id"] = self.cycle_id
        return payload


@dataclass(frozen=True)
class ProviderResult:
    frame: pd.DataFrame
    provenance: ProviderProvenance
    attempted_providers: tuple[str, ...] = ()
