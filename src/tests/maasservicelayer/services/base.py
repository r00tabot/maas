#  Copyright 2024-2025 Canonical Ltd.  This software is licensed under the
#  GNU Affero General Public License version 3 (see the file LICENSE).

import abc

import pytest

from maasservicelayer.db.filters import QuerySpec
from maasservicelayer.exceptions.catalog import (
    NotFoundException,
    PreconditionFailedException,
)
from maasservicelayer.models.base import MaasBaseModel, ResourceBuilder
from maasservicelayer.services.base import BaseService, ReadOnlyService


@pytest.mark.asyncio
class ReadOnlyServiceCommonTests(abc.ABC):
    @pytest.fixture
    @abc.abstractmethod
    def service_instance(self) -> ReadOnlyService:
        pass

    @pytest.fixture
    @abc.abstractmethod
    def test_instance(self) -> MaasBaseModel:
        pass

    async def test_exists(self, service_instance):
        service_instance.repository.exists.return_value = True
        exists = await service_instance.exists(query=QuerySpec())
        assert exists is True
        service_instance.repository.exists.assert_awaited_once_with(
            query=QuerySpec()
        )

    async def test_get_many(self, service_instance):
        service_instance.repository.get_many.return_value = []
        objects = await service_instance.get_many(query=QuerySpec())
        assert objects == []
        service_instance.repository.get_many.assert_awaited_once_with(
            query=QuerySpec()
        )

    async def test_get_one(self, service_instance):
        service_instance.repository.get_one.return_value = None
        obj = await service_instance.get_one(query=QuerySpec())
        assert obj is None
        service_instance.repository.get_one.assert_awaited_once_with(
            query=QuerySpec()
        )

    async def test_get_by_id(self, service_instance):
        service_instance.repository.get_by_id.return_value = None
        obj = await service_instance.get_by_id(0)
        assert obj is None
        service_instance.repository.get_by_id.assert_awaited_once_with(id=0)


@pytest.mark.asyncio
class ServiceCommonTests(ReadOnlyServiceCommonTests):
    @pytest.fixture
    @abc.abstractmethod
    def service_instance(self) -> BaseService:
        pass

    @pytest.fixture
    def builder_model(self) -> type[ResourceBuilder]:
        return ResourceBuilder

    async def test_create(
        self, service_instance, test_instance, builder_model
    ):
        service_instance.repository.create.return_value = test_instance
        builder = builder_model()
        obj = await service_instance.create(builder)
        assert obj == test_instance
        service_instance.repository.create.assert_awaited_once_with(
            builder=builder
        )

    async def test_list(self, service_instance):
        service_instance.repository.list.return_value = []
        objects = await service_instance.list(
            page=1, size=10, query=QuerySpec()
        )
        assert objects == []
        service_instance.repository.list.assert_awaited_once_with(
            page=1, size=10, query=QuerySpec()
        )

    async def test_update_many(
        self, service_instance, test_instance: MaasBaseModel, builder_model
    ):
        service_instance.repository.update_many.return_value = []
        builder = builder_model()
        query = QuerySpec()
        objs = await service_instance.update_many(query, builder)
        assert objs == []
        service_instance.repository.update_many.assert_awaited_once_with(
            query=query, builder=builder
        )

    async def test_update_one(
        self, service_instance, test_instance: MaasBaseModel, builder_model
    ):
        service_instance.repository.get_one.return_value = test_instance
        service_instance.repository.update_by_id.return_value = test_instance
        builder = builder_model()
        query = QuerySpec()
        objs = await service_instance.update_one(query, builder)
        assert objs == test_instance
        service_instance.repository.update_by_id.assert_awaited_once_with(
            id=test_instance.id, builder=builder
        )

    async def test_update_one_not_found(self, service_instance, builder_model):
        service_instance.repository.get_one.return_value = None
        builder = builder_model()
        query = QuerySpec()
        with pytest.raises(NotFoundException):
            await service_instance.update_one(query, builder)

    async def test_update_one_etag_match(
        self, service_instance, test_instance: MaasBaseModel, builder_model
    ):
        service_instance.repository.get_one.return_value = test_instance
        service_instance.repository.update_by_id.return_value = test_instance
        builder = builder_model()
        query = QuerySpec()
        objs = await service_instance.update_one(
            query, builder, test_instance.etag()
        )
        assert objs == test_instance
        service_instance.repository.update_by_id.assert_awaited_once_with(
            id=test_instance.id, builder=builder
        )

    async def test_update_one_etag_not_matching(
        self, service_instance, test_instance: MaasBaseModel, builder_model
    ):
        service_instance.repository.get_one.return_value = test_instance
        builder = builder_model()
        query = QuerySpec()
        with pytest.raises(PreconditionFailedException):
            await service_instance.update_one(query, builder, "not_a_match")

    async def test_update_by_id(
        self, service_instance, test_instance: MaasBaseModel, builder_model
    ):
        service_instance.repository.get_by_id.return_value = test_instance
        service_instance.repository.update_by_id.return_value = test_instance
        builder = builder_model()
        objs = await service_instance.update_by_id(test_instance.id, builder)
        assert objs == test_instance
        service_instance.repository.update_by_id.assert_awaited_once_with(
            id=test_instance.id, builder=builder
        )

    async def test_update_by_id_not_found(
        self, service_instance, builder_model
    ):
        service_instance.repository.get_by_id.return_value = None
        builder = builder_model()
        with pytest.raises(NotFoundException):
            await service_instance.update_by_id(-1, builder)

    async def test_update_by_id_etag_match(
        self, service_instance, test_instance: MaasBaseModel, builder_model
    ):
        service_instance.repository.get_by_id.return_value = test_instance
        service_instance.repository.update_by_id.return_value = test_instance
        builder = builder_model()
        objs = await service_instance.update_by_id(
            test_instance.id, builder, test_instance.etag()
        )
        assert objs == test_instance
        service_instance.repository.update_by_id.assert_awaited_once_with(
            id=test_instance.id, builder=builder
        )

    async def test_update_by_id_etag_not_matching(
        self, service_instance, test_instance: MaasBaseModel, builder_model
    ):
        service_instance.repository.get_by_id.return_value = test_instance
        builder = builder_model()
        with pytest.raises(PreconditionFailedException):
            await service_instance.update_by_id(
                test_instance.id, builder, "not_a_match"
            )

    async def test_delete_many(
        self, service_instance, test_instance: MaasBaseModel
    ):
        service_instance.repository.delete_many.return_value = []
        query = QuerySpec()
        objs = await service_instance.delete_many(query)
        assert objs == []
        service_instance.repository.delete_many.assert_awaited_once_with(
            query=query
        )

    async def test_delete_one(
        self, service_instance, test_instance: MaasBaseModel
    ):
        service_instance.repository.get_one.return_value = test_instance
        service_instance.repository.delete_by_id.return_value = test_instance
        query = QuerySpec()
        deleted_resource = await service_instance.delete_one(query)
        assert deleted_resource == test_instance
        service_instance.repository.delete_by_id.assert_awaited_once_with(
            id=test_instance.id
        )

    async def test_delete_one_not_found(self, service_instance):
        service_instance.repository.get_one.return_value = None
        query = QuerySpec()
        with pytest.raises(NotFoundException):
            await service_instance.delete_one(query)

    async def test_delete_one_etag_match(
        self, service_instance, test_instance: MaasBaseModel
    ):
        service_instance.repository.get_one.return_value = test_instance
        service_instance.repository.delete_by_id.return_value = test_instance
        query = QuerySpec()
        deleted_resource = await service_instance.delete_one(
            query, test_instance.etag()
        )
        assert deleted_resource == test_instance
        service_instance.repository.delete_by_id.assert_awaited_once_with(
            id=test_instance.id
        )

    async def test_delete_one_etag_not_matching(
        self, service_instance, test_instance: MaasBaseModel
    ):
        service_instance.repository.get_one.return_value = test_instance
        query = QuerySpec()
        with pytest.raises(PreconditionFailedException):
            await service_instance.delete_one(query, "not_a_match")

    async def test_delete_by_id(
        self, service_instance, test_instance: MaasBaseModel
    ):
        service_instance.repository.get_by_id.return_value = test_instance
        service_instance.repository.delete_by_id.return_value = test_instance
        deleted_resource = await service_instance.delete_by_id(
            test_instance.id
        )
        assert deleted_resource == test_instance
        service_instance.repository.delete_by_id.assert_awaited_once_with(
            id=test_instance.id
        )

    async def test_delete_by_id_not_found(self, service_instance):
        service_instance.repository.get_by_id.return_value = None
        with pytest.raises(NotFoundException):
            await service_instance.delete_by_id(-1)

    async def test_delete_by_id_etag_match(
        self, service_instance, test_instance: MaasBaseModel
    ):
        service_instance.repository.get_by_id.return_value = test_instance
        service_instance.repository.delete_by_id.return_value = test_instance
        deleted_resource = await service_instance.delete_by_id(
            test_instance.id, test_instance.etag()
        )
        assert deleted_resource == test_instance
        service_instance.repository.delete_by_id.assert_awaited_once_with(
            id=test_instance.id
        )

    async def test_delete_by_id_etag_not_matching(
        self, service_instance, test_instance: MaasBaseModel
    ):
        service_instance.repository.get_by_id.return_value = test_instance
        with pytest.raises(PreconditionFailedException):
            await service_instance.delete_by_id(
                test_instance.id, "not_a_match"
            )
