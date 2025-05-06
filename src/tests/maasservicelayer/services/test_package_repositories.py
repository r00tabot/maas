# Copyright 2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from unittest.mock import Mock

import pytest

from maasservicelayer.context import Context
from maasservicelayer.db.repositories.packagerepositories import (
    PackageRepositoryRepository,
)
from maasservicelayer.models.fields import PackageRepoUrl
from maasservicelayer.models.packagerepositories import PackageRepository
from maasservicelayer.services.events import EventsService
from maasservicelayer.services.packagerepositories import (
    PackageRepositoryService,
)
from maasservicelayer.utils.date import utcnow
from tests.maasservicelayer.services.base import ServiceCommonTests

TEST_PACKAGE_REPO = PackageRepository(
    id=1,
    created=utcnow(),
    updated=utcnow(),
    name="test-main",
    key="test-key",
    url=PackageRepoUrl("http://archive.ubuntu.com/ubuntu"),
    distributions=[],
    components=set(),
    arches=set(),
    disabled_pockets=set(),
    disabled_components=set(),
    disable_sources=False,
    default=True,
    enabled=False,
)


@pytest.mark.asyncio
class TestCommonPackageRepositoriesService(ServiceCommonTests):
    @pytest.fixture
    def service_instance(self) -> PackageRepositoryService:
        return PackageRepositoryService(
            context=Context(),
            repository=Mock(PackageRepositoryRepository),
            events_service=Mock(EventsService),
        )

    @pytest.fixture
    def test_instance(self) -> PackageRepository:
        return TEST_PACKAGE_REPO

    async def test_delete_many(self, service_instance, test_instance):
        with pytest.raises(NotImplementedError):
            await super().test_delete_many(service_instance, test_instance)

    async def test_update_many(self, service_instance, test_instance):
        with pytest.raises(NotImplementedError):
            await super().test_delete_many(service_instance, test_instance)
