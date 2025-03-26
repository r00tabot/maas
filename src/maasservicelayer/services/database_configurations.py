#  Copyright 2025 Canonical Ltd.  This software is licensed under the
#  GNU Affero General Public License version 3 (see the file LICENSE).

from typing import Any

from maasservicelayer.context import Context
from maasservicelayer.db.filters import QuerySpec
from maasservicelayer.db.repositories.database_configurations import (
    DatabaseConfigurationsRepository,
)
from maasservicelayer.services.base import Service


class DatabaseConfigurationsService(Service):
    """
    This service is used only to fetch configurations from the DB!
    Most of the times you want to use the `maasservicelayer.services.entities.configurations service instead.
    """
    def __init__(
        self,
        context: Context,
        database_configurations_repository: DatabaseConfigurationsRepository,
    ):
        super().__init__(context)
        self.database_configurations_repository = (
            database_configurations_repository
        )

    async def get(self, name: str) -> Any:
        configuration = await self.database_configurations_repository.get(name)
        return configuration.value

    async def get_many(self, query: QuerySpec) -> dict[str, Any]:
        configurations = (
            await self.database_configurations_repository.get_many(query)
        )
        return {
            configuration.name: configuration.value
            for configuration in configurations
        }
