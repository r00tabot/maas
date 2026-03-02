# Copyright 2026 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncConnection

from maasservicelayer.builders.usergroups import UserGroupBuilder
from maasservicelayer.context import Context
from maasservicelayer.db._debug import CompiledQuery
from maasservicelayer.db.filters import QuerySpec
from maasservicelayer.db.repositories.usergroups import (
    UserGroupsClauseFactory,
    UserGroupsRepository,
)
from maasservicelayer.db.tables import UserGroupTable
from maasservicelayer.models.usergroups import UserGroup
from tests.fixtures.factories.usergroups import create_test_usergroup
from tests.maasapiserver.fixtures.db import Fixture
from tests.maasservicelayer.db.repositories.base import RepositoryCommonTests


class TestUserGroupsClauseFactory:
    def test_with_ids(self):
        clause = UserGroupsClauseFactory.with_ids([1, 2])
        stmt = (
            select(UserGroupTable.c.id)
            .select_from(UserGroupTable)
            .where(clause.condition)
        )
        assert (
            str(CompiledQuery(stmt).sql)
            == "SELECT maasserver_usergroup.id \nFROM maasserver_usergroup \nWHERE maasserver_usergroup.id IN (__[POSTCOMPILE_id_1])"
        )
        assert CompiledQuery(stmt).params == {"id_1": [1, 2]}

    def test_with_name(self):
        clause = UserGroupsClauseFactory.with_name("test-group")
        stmt = (
            select(UserGroupTable.c.id)
            .select_from(UserGroupTable)
            .where(clause.condition)
        )
        assert (
            str(CompiledQuery(stmt).sql)
            == "SELECT maasserver_usergroup.id \nFROM maasserver_usergroup \nWHERE maasserver_usergroup.name = :name_1"
        )
        assert CompiledQuery(stmt).params == {"name_1": "test-group"}


class TestUserGroupsRepository(RepositoryCommonTests[UserGroup]):
    @pytest.fixture
    def repository_instance(
        self, db_connection: AsyncConnection
    ) -> UserGroupsRepository:
        return UserGroupsRepository(Context(connection=db_connection))

    @pytest.fixture
    async def _setup_test_list(
        self, fixture: Fixture, num_objects: int
    ) -> list[UserGroup]:
        return [
            await create_test_usergroup(
                fixture, name=f"group-{i}", description=f"desc-{i}"
            )
            for i in range(num_objects)
        ]

    @pytest.fixture
    async def created_instance(self, fixture: Fixture) -> UserGroup:
        return await create_test_usergroup(
            fixture, name="mygroup", description="description"
        )

    @pytest.fixture
    async def instance_builder_model(self) -> type[UserGroupBuilder]:
        return UserGroupBuilder

    @pytest.fixture
    async def instance_builder(self) -> UserGroupBuilder:
        return UserGroupBuilder(name="name", description="description")

    async def test_list_with_filters(
        self,
        repository_instance: UserGroupsRepository,
        fixture: Fixture,
    ) -> None:
        group1 = await create_test_usergroup(
            fixture, name="group-a", description="a"
        )
        group2 = await create_test_usergroup(
            fixture, name="group-b", description="b"
        )

        query = QuerySpec(where=UserGroupsClauseFactory.with_ids([group1.id]))
        groups = await repository_instance.list(1, 20, query)
        assert len(groups.items) == 1
        assert groups.total == 1
        assert groups.items[0].id == group1.id

        query = QuerySpec(
            where=UserGroupsClauseFactory.with_ids([group1.id, group2.id])
        )
        groups = await repository_instance.list(1, 20, query)
        assert len(groups.items) == 2
        assert groups.total == 2
