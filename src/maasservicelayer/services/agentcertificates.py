# Copyright 2025 Canonical Ltd. This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from maasservicelayer.context import Context
from maasservicelayer.db.repositories.agentcertificates import (
    AgentCertificatesRepository,
)
from maasservicelayer.models.agentcertificates import AgentCertificate
from maasservicelayer.services.base import ReadOnlyService


class AgentCertificateService(
    ReadOnlyService[AgentCertificate, AgentCertificatesRepository]
):
    def __init__(
        self,
        context: Context,
        repository: AgentCertificatesRepository,
    ):
        super().__init__(context, repository)
