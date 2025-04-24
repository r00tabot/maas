# Copyright 2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from typing import Type

from sqlalchemy import Table

from maasservicelayer.db.repositories.base import ViewRepository
from maasservicelayer.db.tables import DiscoveryView
from maasservicelayer.models.discoveries import Discovery


class DiscoveriesRepository(ViewRepository[Discovery]):
    def get_repository_table(self) -> Table:
        return DiscoveryView

    def get_model_factory(self) -> Type[Discovery]:
        return Discovery
