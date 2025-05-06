# Copyright 2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from maasservicelayer.context import Context
from maasservicelayer.db.repositories.packagerepositories import (
    PackageRepositoryRepository,
)
from maasservicelayer.models.packagerepositories import PackageRepository
from tests.fixtures.factories.package_repositories import (
    create_test_package_repository,
)
from tests.maasapiserver.fixtures.db import Fixture
from tests.maasservicelayer.db.repositories.base import RepositoryCommonTests


class TestCommonPackageRepository(RepositoryCommonTests[PackageRepository]):
    @pytest.fixture
    def repository_instance(
        self, db_connection: AsyncConnection
    ) -> PackageRepositoryRepository:
        return PackageRepositoryRepository(
            context=Context(connection=db_connection)
        )

    @pytest.fixture
    async def _setup_test_list(
        self, fixture: Fixture, num_objects: int
    ) -> list[PackageRepository]:
        return [
            await create_test_package_repository(
                fixture, name=f"test-{i}", default=False
            )
            for i in range(num_objects)
        ]

    @pytest.fixture
    async def instance_builder(self, *args, **kwargs) -> ResourceBuilder:
        pass

    @pytest.fixture
    async def instance_builder_model(self) -> type[ResourceBuilder]:
        pass
