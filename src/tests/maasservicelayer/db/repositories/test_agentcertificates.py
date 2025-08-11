# Copyright 2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import pytest
from sqlalchemy.ext.asyncio import AsyncConnection

from maasservicelayer.context import Context
from maasservicelayer.db.repositories.agentcertificates import (
    AgentCertificatesRepository,
)
from maasservicelayer.models.agentcertificates import AgentCertificate
from tests.fixtures.factories.agentcertificates import (
    create_test_agentcertificates_entry,
)
from tests.fixtures.factories.agents import create_test_agents_entry
from tests.fixtures.factories.node import create_test_rack_controller_entry
from tests.fixtures.factories.racks import create_test_rack_entry
from tests.maasservicelayer.db.repositories.base import (
    Fixture,
    ReadOnlyRepositoryCommonTests,
)


class TestAgentCertificatesRepository(
    ReadOnlyRepositoryCommonTests[AgentCertificate]
):
    @pytest.fixture
    async def _setup_test_list(
        self, fixture: Fixture, num_objects: int
    ) -> list[AgentCertificate]:
        agentcertificates = []

        for i in range(num_objects):
            rack = await create_test_rack_entry(fixture, name=f"rack-{i}")
            rack_controllers = await create_test_rack_controller_entry(fixture)
            agent = await create_test_agents_entry(
                fixture,
                secret=f"secret-{i}",
                rack_id=rack.id,
                rackcontroller_id=rack_controllers["id"],
            )
            agentcertificates.append(
                await create_test_agentcertificates_entry(
                    fixture,
                    certificate=f"certificate-{i}".encode("utf-8"),
                    certificate_fingerprint=f"fingerprint-{i}",
                    agent_id=agent.id,
                )
            )
        return agentcertificates

    @pytest.fixture
    async def created_instance(self, fixture: Fixture) -> AgentCertificate:
        rack = await create_test_rack_entry(fixture, name="rack")
        rack_controller = await create_test_rack_controller_entry(fixture)
        agent = await create_test_agents_entry(
            fixture,
            secret="secret",
            rack_id=rack.id,
            rackcontroller_id=rack_controller["id"],
        )

        return await create_test_agentcertificates_entry(
            fixture,
            certificate=b"certificate",
            certificate_fingerprint="fingerprint",
            agent_id=agent.id,
        )

    @pytest.fixture
    async def repository_instance(
        self, db_connection: AsyncConnection
    ) -> AgentCertificatesRepository:
        return AgentCertificatesRepository(Context(connection=db_connection))
