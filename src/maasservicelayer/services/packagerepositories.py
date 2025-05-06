# Copyright 2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from typing import List

from maascommon.enums.events import EventTypeEnum
from maasservicelayer.builders.packagerepositories import (
    PackageRepositoryBuilder,
)
from maasservicelayer.context import Context
from maasservicelayer.db.repositories.packagerepositories import (
    PackageRepositoryRepository,
)
from maasservicelayer.models.packagerepositories import PackageRepository
from maasservicelayer.services.base import BaseService, ServiceCache
from maasservicelayer.services.events import EventsService


class PackageRepositoryService(
    BaseService[
        PackageRepository,
        PackageRepositoryRepository,
        PackageRepositoryBuilder,
    ]
):
    def __init__(
        self,
        context: Context,
        repository: PackageRepositoryRepository,
        events_service: EventsService,
        cache: ServiceCache | None = None,
    ):
        self.events_service = events_service
        super().__init__(context, repository, cache)

    async def post_create_hook(self, resource: PackageRepository) -> None:
        await self.events_service.record_event(
            event_type=EventTypeEnum.SETTINGS,
            event_description=f"Created package repository {resource.name}",
        )

    async def post_update_hook(
        self,
        old_resource: PackageRepository,
        updated_resource: PackageRepository,
    ) -> None:
        await self.events_service.record_event(
            event_type=EventTypeEnum.SETTINGS,
            event_description=f"Updated package repository {updated_resource.name}",
        )

    async def post_update_many_hook(
        self, resources: List[PackageRepository]
    ) -> None:
        raise NotImplementedError()

    async def post_delete_hook(self, resource: PackageRepository) -> None:
        await self.events_service.record_event(
            event_type=EventTypeEnum.SETTINGS,
            event_description=f"Deleted package repository {resource.name}",
        )

    async def post_delete_many_hook(
        self, resources: List[PackageRepository]
    ) -> None:
        raise NotImplementedError()
