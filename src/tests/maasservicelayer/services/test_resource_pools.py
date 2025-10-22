#  Copyright 2024 Canonical Ltd.  This software is licensed under the
#  GNU Affero General Public License version 3 (see the file LICENSE).

from unittest.mock import Mock

import pytest

from maascommon.logging.security import AUTHZ_ADMIN, SECURITY
from maasservicelayer.context import Context
from maasservicelayer.db.repositories.resource_pools import (
    ResourcePoolRepository,
)
from maasservicelayer.exceptions.catalog import BadRequestException
from maasservicelayer.models.base import MaasBaseModel
from maasservicelayer.models.resource_pools import ResourcePool
from maasservicelayer.services import resource_pools as resource_pools_module
from maasservicelayer.services import ResourcePoolsService
from maasservicelayer.services.base import BaseService
from maasservicelayer.utils.date import utcnow
from tests.fixtures import MockLoggerMixin
from tests.maasservicelayer.services.base import ServiceCommonTests


@pytest.mark.asyncio
class TestCommonResourcePoolsService(ServiceCommonTests, MockLoggerMixin):
    module = resource_pools_module

    @pytest.fixture
    def service_instance(self) -> BaseService:
        return ResourcePoolsService(
            context=Context(),
            resource_pools_repository=Mock(ResourcePoolRepository),
        )

    @pytest.fixture
    def test_instance(self) -> MaasBaseModel:
        return ResourcePool(
            id=2,
            name="test",
            description="",
            created=utcnow(),
            updated=utcnow(),
        )

    async def test_post_create_hook(
        self,
        service_instance: BaseService,
        test_instance: MaasBaseModel,
        mock_logger: Mock,
    ):
        await service_instance.post_create_hook(test_instance)
        mock_logger.info.assert_called_with(
            f"{AUTHZ_ADMIN}:resourcepool:created:{test_instance.id}",
            type=SECURITY,
        )

    async def test_post_update_hook(
        self,
        service_instance: BaseService,
        test_instance: MaasBaseModel,
        mock_logger: Mock,
    ):
        await service_instance.post_update_hook(test_instance, test_instance)
        mock_logger.info.assert_called_with(
            f"{AUTHZ_ADMIN}:resourcepool:updated:{test_instance.id}",
            type=SECURITY,
        )

    async def test_post_update_many_hook(
        self,
        service_instance: BaseService,
        test_instance: MaasBaseModel,
        mock_logger: Mock,
    ):
        await service_instance.post_update_many_hook([test_instance])
        mock_logger.info.assert_called_with(
            f"{AUTHZ_ADMIN}:resourcepools:updated:{[test_instance.id]}",
            type=SECURITY,
        )

    async def test_post_delete_hook(
        self,
        service_instance: BaseService,
        test_instance: MaasBaseModel,
        mock_logger: Mock,
    ):
        await service_instance.post_delete_hook(test_instance)
        mock_logger.info.assert_called_with(
            f"{AUTHZ_ADMIN}:resourcepool:deleted:{test_instance.id}",
            type=SECURITY,
        )

    async def test_post_delete_many_hook(
        self,
        service_instance: BaseService,
        test_instance: MaasBaseModel,
        mock_logger: Mock,
    ):
        await service_instance.post_delete_many_hook([test_instance])
        mock_logger.info.assert_called_with(
            f"{AUTHZ_ADMIN}:resourcepools:deleted:{[test_instance.id]}",
            type=SECURITY,
        )


@pytest.mark.asyncio
class TestResourcePoolsService:
    async def test_list_ids(self) -> None:
        resource_pool_repository_mock = Mock(ResourcePoolRepository)
        resource_pool_repository_mock.list_ids.return_value = {1, 2, 3}
        resource_pools_service = ResourcePoolsService(
            context=Context(),
            resource_pools_repository=resource_pool_repository_mock,
        )
        ids_list = await resource_pools_service.list_ids()
        resource_pool_repository_mock.list_ids.assert_called_once()
        assert ids_list == {1, 2, 3}

    async def test_cannot_delete_default_resourcepool(self) -> None:
        resource_pools_repository = Mock(ResourcePoolRepository)
        resource_pools_service = ResourcePoolsService(
            context=Context(),
            resource_pools_repository=resource_pools_repository,
        )
        resource_pool = ResourcePool(id=0, name="default", description="")
        with pytest.raises(BadRequestException):
            await resource_pools_service.pre_delete_hook(resource_pool)
