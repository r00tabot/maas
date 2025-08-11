# Copyright 2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import datetime
from typing import Optional

from maasservicelayer.models.base import MaasBaseModel


class AgentCertificate(MaasBaseModel):
    certificate_fingerprint: str
    certificate: bytes
    revoked_at: Optional[datetime.datetime]
    agent_id: int
