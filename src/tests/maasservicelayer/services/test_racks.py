# Copyright 2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from unittest.mock import Mock

import pytest

from maasservicelayer.context import Context
from maasservicelayer.db.repositories.racks import RacksRepository
from maasservicelayer.models.racks import Rack
from maasservicelayer.services.racks import RacksService
from maasservicelayer.utils.date import utcnow
from tests.maasservicelayer.services.base import ServiceCommonTests


@pytest.mark.asyncio
class TestRacksService(ServiceCommonTests):
    @pytest.fixture
    def service_instance(self) -> RacksService:
        return RacksService(
            context=Context(), repository=Mock(RacksRepository)
        )

    @pytest.fixture
    def test_instance(self) -> Rack:
        now = utcnow()
        return Rack(id=1, created=now, updated=now, name="rack")
