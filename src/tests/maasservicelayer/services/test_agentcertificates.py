# Copyright 2025 Canonical Ltd. This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from unittest.mock import Mock

import pytest

from maasservicelayer.context import Context
from maasservicelayer.db.repositories.agentcertificates import (
    AgentCertificatesRepository,
)
from maasservicelayer.models.agentcertificates import AgentCertificate
from maasservicelayer.services.agentcertificates import AgentCertificateService
from tests.maasservicelayer.services.base import ReadOnlyServiceCommonTests


class TestAgentCertificateService(ReadOnlyServiceCommonTests):
    @pytest.fixture
    def service_instance(self) -> AgentCertificateService:
        return AgentCertificateService(
            context=Context(),
            repository=Mock(AgentCertificatesRepository),
        )

    @pytest.fixture
    def test_instance(self) -> AgentCertificate:
        return AgentCertificate(
            certificate=b"certificate",
            certificate_fingerprint="fingerprint",
            agent_id=10,
            revoked_at=None,
        )
