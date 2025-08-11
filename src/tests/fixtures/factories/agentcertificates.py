# Copyright 2025 Canonical Ltd. This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from maasservicelayer.db.tables import AgentCertificateTable
from maasservicelayer.models.agentcertificates import AgentCertificate
from tests.maasapiserver.fixtures.db import Fixture


async def create_test_agentcertificates_entry(
    fixture: Fixture,
    certificate: bytes,
    certificate_fingerprint: str,
    agent_id: int,
    **extra_details,
) -> AgentCertificate:
    agentcertificate = {
        "certificate": certificate,
        "certificate_fingerprint": certificate_fingerprint,
        "agent_id": agent_id,
        "revoked_at": None,
    }
    agentcertificate.update(extra_details)

    [created_agentcertificate] = await fixture.create(
        AgentCertificateTable.name, agentcertificate
    )

    return AgentCertificate(**created_agentcertificate)
