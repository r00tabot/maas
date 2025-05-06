# Copyright 2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from typing import Any

from maasservicelayer.db.tables import PackageRepositoryTable
from maasservicelayer.models.packagerepositories import PackageRepository
from tests.maasapiserver.fixtures.db import Fixture


async def create_test_package_repository(
    fixture: Fixture, extra_details: dict[str, Any]
) -> PackageRepository:
    package_repo = {
        "name": "test-main",
        "key": "test-key",
        "url": "http://archive.ubuntu.com/ubuntu",
        "distributions": [],
        "components": set(),
        "arches": set(),
        "disabled_pockets": set(),
        "disabled_components": set(),
        "disable_sources": False,
        "default": True,
        "enabled": False,
    }
    package_repo.update(extra_details)

    [package_repo] = await fixture.create(PackageRepositoryTable, package_repo)
    return PackageRepository(**package_repo)
