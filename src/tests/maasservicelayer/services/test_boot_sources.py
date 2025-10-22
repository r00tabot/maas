# Copyright 2025 Canonical Ltd. This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from unittest.mock import Mock

import pytest

from maascommon.logging.security import AUTHZ_ADMIN, SECURITY
from maasservicelayer.context import Context
from maasservicelayer.db.filters import QuerySpec
from maasservicelayer.db.repositories.bootsourcecache import (
    BootSourceCacheClauseFactory,
)
from maasservicelayer.db.repositories.bootsources import BootSourcesRepository
from maasservicelayer.db.repositories.bootsourceselections import (
    BootSourceSelectionClauseFactory,
)
from maasservicelayer.models.bootsources import BootSource
from maasservicelayer.services import boot_sources as boot_sources_module
from maasservicelayer.services.boot_sources import BootSourcesService
from maasservicelayer.services.bootsourcecache import BootSourceCacheService
from maasservicelayer.services.bootsourceselections import (
    BootSourceSelectionsService,
)
from maasservicelayer.services.configurations import ConfigurationsService
from maasservicelayer.services.events import EventsService
from maasservicelayer.utils.date import utcnow
from tests.fixtures import MockLoggerMixin
from tests.maasservicelayer.services.base import ServiceCommonTests


@pytest.mark.asyncio
class TestBootSourcesService(ServiceCommonTests, MockLoggerMixin):
    module = boot_sources_module

    @pytest.fixture
    def service_instance(self) -> BootSourcesService:
        return BootSourcesService(
            context=Context(),
            repository=Mock(BootSourcesRepository),
            boot_source_cache_service=Mock(BootSourceCacheService),
            boot_source_selections_service=Mock(BootSourceSelectionsService),
            configuration_service=Mock(ConfigurationsService),
            events_service=Mock(EventsService),
        )

    @pytest.fixture
    def test_instance(self) -> BootSource:
        now = utcnow()
        return BootSource(
            id=1,
            created=now,
            updated=now,
            url="http://example.com",
            keyring_filename="/path/to/keyring_file.gpg",
            keyring_data=b"",
            priority=10,
            skip_keyring_verification=False,
        )

    async def test_delete(self, test_instance):
        boot_source = test_instance

        repository_mock = Mock(BootSourcesRepository)
        repository_mock.get_one.return_value = boot_source
        repository_mock.delete_by_id.return_value = boot_source

        boot_source_cache_service_mock = Mock(BootSourceCacheService)
        boot_source_selections_service_mock = Mock(BootSourceSelectionsService)
        configuration_service_mock = Mock(ConfigurationsService)
        events_service_mock = Mock(EventsService)

        boot_source_service = BootSourcesService(
            context=Context(),
            repository=repository_mock,
            boot_source_cache_service=boot_source_cache_service_mock,
            boot_source_selections_service=boot_source_selections_service_mock,
            configuration_service=configuration_service_mock,
            events_service=events_service_mock,
        )

        query = Mock(QuerySpec)
        await boot_source_service.delete_one(query)

        repository_mock.delete_by_id.assert_called_once_with(id=boot_source.id)

        boot_source_cache_service_mock.delete_many.assert_called_once_with(
            query=QuerySpec(
                where=BootSourceCacheClauseFactory.with_boot_source_id(
                    boot_source.id
                )
            )
        )
        boot_source_selections_service_mock.delete_many.assert_called_once_with(
            query=QuerySpec(
                where=BootSourceSelectionClauseFactory.with_boot_source_id(
                    boot_source.id
                )
            )
        )

    async def test_post_create_hook(
        self,
        test_instance: BootSource,
        service_instance: BootSourcesService,
        mock_logger: Mock,
    ):
        await service_instance.post_create_hook(test_instance)
        mock_logger.info.assert_called_with(
            f"{AUTHZ_ADMIN}:bootsource:created:{test_instance.id}",
            type=SECURITY,
        )

    async def test_post_updated_hook(
        self,
        test_instance: BootSource,
        service_instance: BootSourcesService,
        mock_logger: Mock,
    ):
        await service_instance.post_update_hook(test_instance, test_instance)
        mock_logger.info.assert_called_with(
            f"{AUTHZ_ADMIN}:bootsource:updated:{test_instance.id}",
            type=SECURITY,
        )

    async def test_post_delete_hook(
        self,
        test_instance: BootSource,
        service_instance: BootSourcesService,
        mock_logger: Mock,
    ):
        await service_instance.post_delete_hook(test_instance)
        mock_logger.info.assert_called_with(
            f"{AUTHZ_ADMIN}:bootsource:deleted:{test_instance.id}",
            type=SECURITY,
        )
