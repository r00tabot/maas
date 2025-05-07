# Copyright 2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import pytest

from maasapiserver.v3.api.public.models.requests.package_repositories import (
    PackageRepositoryCreateRequest,
    PackageRepositoryUpdateRequest,
)
from maascommon.enums.package_repositories import (
    ComponentsToDisableEnum,
    KnownComponentsEnum,
    PACKAGE_REPO_MAIN_ARCHES,
    PACKAGE_REPO_PORTS_ARCHES,
)
from maasservicelayer.exceptions.catalog import ValidationException
from maasservicelayer.models.fields import PackageRepoUrl


class TestPackageRepositoryCreateRequest:
    @pytest.mark.parametrize("name", ["test", "main_archive", "ports_archive"])
    def test_populate_arches(self, name: str):
        r = PackageRepositoryCreateRequest(
            name=name, url=PackageRepoUrl("ppa:foo/bar"), disable_sources=True
        )
        if name == "ports_archive":
            assert r.arches == PACKAGE_REPO_PORTS_ARCHES
        else:
            assert r.arches == PACKAGE_REPO_MAIN_ARCHES

    def test_to_builder(self):
        r = PackageRepositoryCreateRequest(
            name="test",
            url=PackageRepoUrl("ppa:foo/bar"),
            disable_sources=True,
        )
        b = r.to_builder()
        assert b.name == r.name
        assert b.key == r.key
        assert b.url == r.url
        assert b.distributions == r.distributions
        assert b.components == r.components
        assert b.arches == r.arches
        assert b.disabled_pockets == r.disabled_pockets
        assert b.disabled_components == r.disabled_components
        assert b.enabled == r.enabled
        assert b.default is False


class TestPackageRepositoryUpdateRequest:
    @pytest.mark.parametrize(
        "default,enabled,should_raise",
        [
            (True, True, False),
            (False, False, False),
            (False, True, False),
            (True, False, True),
        ],
    )
    def test_validate_enabled(
        self, default: bool, enabled: bool, should_raise: bool
    ):
        r = PackageRepositoryUpdateRequest(
            name="test",
            url=PackageRepoUrl("ppa:foo/bar"),
            disable_sources=True,
            enabled=enabled,
        )
        if should_raise:
            with pytest.raises(ValidationException):
                r.validate_enabled(is_default=default)
        else:
            r.validate_enabled(is_default=default)

    @pytest.mark.parametrize(
        "default,components,disabled_components,should_raise",
        [
            (True, {KnownComponentsEnum.UNIVERSE}, set(), True),
            (False, {KnownComponentsEnum.UNIVERSE}, set(), False),
            (False, set(), {ComponentsToDisableEnum.RESTRICTED}, True),
            (True, set(), {ComponentsToDisableEnum.RESTRICTED}, False),
        ],
    )
    def test_validate_components(
        self,
        default: bool,
        components: set[KnownComponentsEnum],
        disabled_components: set[ComponentsToDisableEnum],
        should_raise: bool,
    ):
        r = PackageRepositoryUpdateRequest(
            name="test",
            url=PackageRepoUrl("ppa:foo/bar"),
            disable_sources=True,
            enabled=True,
            components=components,
            disabled_components=disabled_components,
        )
        if should_raise:
            with pytest.raises(ValidationException):
                r.validate_components(is_default=default)
        else:
            r.validate_components(is_default=default)
