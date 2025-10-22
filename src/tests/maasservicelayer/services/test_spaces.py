# Copyright 2024 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from unittest.mock import Mock

import pytest

from maascommon.logging.security import AUTHZ_ADMIN, SECURITY
from maasservicelayer.context import Context
from maasservicelayer.db.repositories.spaces import SpacesRepository
from maasservicelayer.models.base import MaasBaseModel
from maasservicelayer.models.spaces import Space
from maasservicelayer.services import spaces as spaces_module
from maasservicelayer.services.base import BaseService
from maasservicelayer.services.spaces import SpacesService
from maasservicelayer.services.vlans import VlansService
from maasservicelayer.utils.date import utcnow
from tests.fixtures import MockLoggerMixin
from tests.maasservicelayer.services.base import ServiceCommonTests


@pytest.mark.asyncio
class TestCommonSpacesService(ServiceCommonTests, MockLoggerMixin):
    module = spaces_module

    @pytest.fixture
    def service_instance(self) -> BaseService:
        return SpacesService(
            context=Context(),
            vlans_service=Mock(VlansService),
            spaces_repository=Mock(SpacesRepository),
        )

    @pytest.fixture
    def test_instance(self) -> MaasBaseModel:
        return Space(
            id=1,
            name="test_space_name",
            description="test_space_description",
            created=utcnow(),
            updated=utcnow(),
        )

    async def test_delete_many(
        self, service_instance, test_instance: MaasBaseModel
    ):
        with pytest.raises(NotImplementedError):
            await super().test_delete_many(service_instance, test_instance)

    async def test_post_create_hook(
        self,
        service_instance: BaseService,
        test_instance: MaasBaseModel,
        mock_logger: Mock,
    ):
        await service_instance.post_create_hook(test_instance)
        mock_logger.info.assert_called_with(
            f"{AUTHZ_ADMIN}:space:created:{test_instance.id}",
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
            f"{AUTHZ_ADMIN}:space:updated:{test_instance.id}",
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
            f"{AUTHZ_ADMIN}:spaces:updated:{[test_instance.id]}",
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
            f"{AUTHZ_ADMIN}:space:deleted:{test_instance.id}",
            type=SECURITY,
        )
