# Copyright 2024-2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).
from typing import List

import structlog

from maascommon.logging.security import AUTHZ_ADMIN, SECURITY
from maasservicelayer.builders.spaces import SpaceBuilder
from maasservicelayer.builders.vlans import VlanBuilder
from maasservicelayer.context import Context
from maasservicelayer.db.filters import QuerySpec
from maasservicelayer.db.repositories.spaces import SpacesRepository
from maasservicelayer.db.repositories.vlans import VlansClauseFactory
from maasservicelayer.models.spaces import Space
from maasservicelayer.services.base import BaseService
from maasservicelayer.services.vlans import VlansService

logger = structlog.getLogger()


class SpacesService(BaseService[Space, SpacesRepository, SpaceBuilder]):
    def __init__(
        self,
        context: Context,
        vlans_service: VlansService,
        spaces_repository: SpacesRepository,
    ):
        super().__init__(context, spaces_repository)
        self.vlans_service = vlans_service

    async def post_create_hook(self, resource):
        logger.info(
            f"{AUTHZ_ADMIN}:space:created:{resource.id}",
            type=SECURITY,
        )

    async def post_update_hook(self, old_resource, updated_resource):
        logger.info(
            f"{AUTHZ_ADMIN}:space:updated:{updated_resource.id}",
            type=SECURITY,
        )

    async def post_update_many_hook(self, resources):
        resource_ids = [resource.id for resource in resources]
        logger.info(
            f"{AUTHZ_ADMIN}:spaces:updated:{resource_ids}",
            type=SECURITY,
        )

    async def post_delete_hook(self, resource: Space) -> None:
        # Remove this space's id from all related VLANs
        await self.vlans_service.update_many(
            query=QuerySpec(
                where=VlansClauseFactory.with_space_id(resource.id)
            ),
            builder=VlanBuilder(space_id=None),
        )
        logger.info(
            f"{AUTHZ_ADMIN}:space:deleted:{resource.id}",
            type=SECURITY,
        )

    async def post_delete_many_hook(self, resources: List[Space]) -> None:
        raise NotImplementedError("Not implemented yet.")
