from __future__ import annotations

import pandas as pd

from lucerna_core.domain.models import MissingData
from lucerna_core.providers.capabilities import ProviderAuthorityLevel
from lucerna_core.providers.contracts_v2 import DataProviderPortV2
from lucerna_core.providers.query import DataQuery
from lucerna_core.providers.result import (
    ProviderFailureStatus,
    ProviderProvenance,
    ProviderResult,
    utc_now_iso,
)


class ProviderRegistryV2:
    def __init__(self, providers: list[DataProviderPortV2]) -> None:
        self._providers = providers

    @property
    def providers(self) -> tuple[DataProviderPortV2, ...]:
        return tuple(self._providers)

    def list_provider_ids(self) -> tuple[str, ...]:
        return tuple(provider.provider_id for provider in self._providers)

    def fetch(
        self,
        query: DataQuery,
        *,
        allow_fallback: bool = True,
        cross_check_providers: tuple[str, ...] = (),
    ) -> ProviderResult:
        warnings: list[str] = []
        attempted: list[str] = []
        primary_result: ProviderResult | None = None

        for index, provider in enumerate(self._providers):
            attempted.append(provider.provider_id)
            if not provider.supports_query(query):
                warnings.append(f"{provider.provider_id}: missing_capability")
                continue
            try:
                result = provider.fetch(query)
            except MissingData as exc:
                warnings.append(f"{provider.provider_id}: {exc}")
                continue

            if result.provenance.failure_status != ProviderFailureStatus.OK:
                warnings.append(
                    f"{provider.provider_id}: {result.provenance.failure_status.value}"
                )
                if result.provenance.warnings:
                    warnings.extend(result.provenance.warnings)
                if result.frame.empty:
                    continue

            authority = provider.authority_level
            if index > 0 and authority == ProviderAuthorityLevel.PRIMARY:
                authority = ProviderAuthorityLevel.FALLBACK

            merged_provenance = ProviderProvenance(
                provider_id=result.provenance.provider_id,
                authority_level=authority,
                data_kind=result.provenance.data_kind,
                asset_domain=result.provenance.asset_domain,
                captured_at=result.provenance.captured_at,
                as_of=result.provenance.as_of,
                source_timestamp=result.provenance.source_timestamp,
                cache_hit=result.provenance.cache_hit,
                cache_policy=result.provenance.cache_policy,
                quota_policy=result.provenance.quota_policy,
                failure_status=result.provenance.failure_status,
                session_model=result.provenance.session_model or query.session_model,
                checkpoint_id=result.provenance.checkpoint_id or query.checkpoint_id,
                cycle_id=result.provenance.cycle_id or query.cycle_id,
                warnings=tuple(warnings) + result.provenance.warnings,
            )
            primary_result = ProviderResult(
                frame=result.frame,
                provenance=merged_provenance,
                attempted_providers=tuple(attempted),
            )
            break

        if primary_result is None:
            if not allow_fallback:
                return self._empty_result(query, attempted, warnings, ProviderFailureStatus.EMPTY)
            return self._empty_result(query, attempted, warnings, ProviderFailureStatus.EMPTY)

        if cross_check_providers:
            primary_result = self._apply_cross_checks(
                query,
                primary_result,
                cross_check_providers,
                warnings,
            )

        return primary_result

    def _apply_cross_checks(
        self,
        query: DataQuery,
        primary: ProviderResult,
        cross_check_providers: tuple[str, ...],
        warnings: list[str],
    ) -> ProviderResult:
        extra_warnings = list(primary.provenance.warnings)
        for provider_id in cross_check_providers:
            provider = self._provider_by_id(provider_id)
            if provider is None:
                extra_warnings.append(f"cross_check: unknown provider {provider_id}")
                continue
            if not provider.supports_query(query):
                extra_warnings.append(f"cross_check:{provider_id}: missing_capability")
                continue
            try:
                check = provider.fetch(query)
            except MissingData as exc:
                extra_warnings.append(f"cross_check:{provider_id}: {exc}")
                continue
            if check.frame.empty:
                extra_warnings.append(f"cross_check:{provider_id}: empty")
                continue
            if not primary.frame.empty and not check.frame.equals(primary.frame):
                extra_warnings.append(
                    f"cross_check:{provider_id}: frame mismatch with primary "
                    f"{primary.provenance.provider_id}"
                )
        return ProviderResult(
            frame=primary.frame,
            provenance=ProviderProvenance(
                provider_id=primary.provenance.provider_id,
                authority_level=primary.provenance.authority_level,
                data_kind=primary.provenance.data_kind,
                asset_domain=primary.provenance.asset_domain,
                captured_at=primary.provenance.captured_at,
                as_of=primary.provenance.as_of,
                source_timestamp=primary.provenance.source_timestamp,
                cache_hit=primary.provenance.cache_hit,
                cache_policy=primary.provenance.cache_policy,
                quota_policy=primary.provenance.quota_policy,
                failure_status=primary.provenance.failure_status,
                session_model=primary.provenance.session_model,
                checkpoint_id=primary.provenance.checkpoint_id,
                cycle_id=primary.provenance.cycle_id,
                warnings=tuple(extra_warnings),
            ),
            attempted_providers=primary.attempted_providers,
        )

    def _provider_by_id(self, provider_id: str) -> DataProviderPortV2 | None:
        for provider in self._providers:
            if provider.provider_id == provider_id:
                return provider
        return None

    def _empty_result(
        self,
        query: DataQuery,
        attempted: list[str],
        warnings: list[str],
        failure_status: ProviderFailureStatus,
    ) -> ProviderResult:
        return ProviderResult(
            frame=pd.DataFrame(),
            provenance=ProviderProvenance(
                provider_id="none",
                authority_level=ProviderAuthorityLevel.FALLBACK,
                data_kind=query.data_kind,
                asset_domain=query.asset_domain,
                captured_at=utc_now_iso(),
                as_of=query.as_of,
                failure_status=failure_status,
                session_model=query.session_model,
                checkpoint_id=query.checkpoint_id,
                cycle_id=query.cycle_id,
                warnings=tuple(warnings),
            ),
            attempted_providers=tuple(attempted),
        )
