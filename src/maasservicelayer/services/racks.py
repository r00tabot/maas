# Copyright 2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from maasservicelayer.builders.racks import RackBuilder
from maasservicelayer.context import Context
from maasservicelayer.db.repositories.racks import RacksRepository
from maasservicelayer.models.racks import Rack
from maasservicelayer.services.base import BaseService


class RacksService(BaseService[Rack, RacksRepository, RackBuilder]):
    def __init__(self, context: Context, repository: RacksRepository) -> None:
        super().__init__(context, repository)
