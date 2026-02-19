# Copyright 2026 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from dataclasses import dataclass

from maascommon.openfga.client.client import OpenFGAClient
from maasservicelayer.builders.openfga_tuple import OpenFGATupleBuilder
from maasservicelayer.context import Context
from maasservicelayer.db.filters import QuerySpec
from maasservicelayer.db.repositories.openfga_tuples import (
    OpenFGATuplesRepository,
)
from maasservicelayer.models.openfga_tuple import OpenFGATuple
from maasservicelayer.services.base import Service, ServiceCache


@dataclass(slots=True)
class OpenFGAServiceCache(ServiceCache):
    client: OpenFGAClient | None = None

    async def close(self) -> None:
        if self.client:
            await self.client.close()


class OpenFGATupleService(Service):
    def __init__(
        self,
        context: Context,
        openfga_tuple_repository: OpenFGATuplesRepository,
        cache: ServiceCache,
    ):
        super().__init__(context, cache)
        self.openfga_tuple_repository = openfga_tuple_repository
        self._client = None

    @staticmethod
    def build_cache_object() -> OpenFGAServiceCache:
        return OpenFGAServiceCache()

    @Service.from_cache_or_execute(attr="client")
    async def get_client(self) -> OpenFGAClient:
        if self._client:
            return self._client

        self._client = OpenFGAClient()
        return self._client

    async def create(self, builder: OpenFGATupleBuilder) -> OpenFGATuple:
        return await self.openfga_tuple_repository.create(builder)

    async def delete_many(self, query: QuerySpec) -> None:
        return await self.openfga_tuple_repository.delete_many(query)
