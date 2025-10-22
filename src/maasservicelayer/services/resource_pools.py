#  Copyright 2024-2025 Canonical Ltd.  This software is licensed under the
#  GNU Affero General Public License version 3 (see the file LICENSE).

import structlog

from maascommon.logging.security import AUTHZ_ADMIN, SECURITY
from maasservicelayer.builders.resource_pools import ResourcePoolBuilder
from maasservicelayer.context import Context
from maasservicelayer.db.filters import QuerySpec
from maasservicelayer.db.repositories.resource_pools import (
    ResourcePoolRepository,
)
from maasservicelayer.exceptions.catalog import (
    BadRequestException,
    BaseExceptionDetail,
)
from maasservicelayer.exceptions.constants import (
    CANNOT_DELETE_DEFAULT_RESOURCEPOOL_VIOLATION_TYPE,
)
from maasservicelayer.models.base import ListResult
from maasservicelayer.models.resource_pools import (
    ResourcePool,
    ResourcePoolWithSummary,
)
from maasservicelayer.services.base import BaseService

logger = structlog.getLogger()


class ResourcePoolsService(
    BaseService[ResourcePool, ResourcePoolRepository, ResourcePoolBuilder]
):
    def __init__(
        self,
        context: Context,
        resource_pools_repository: ResourcePoolRepository,
    ):
        super().__init__(context, resource_pools_repository)

    async def list_ids(self) -> set[int]:
        """Returns all the ids of the resource pools in the db."""
        return await self.repository.list_ids()

    async def list_with_summary(
        self, page: int, size: int, query: QuerySpec | None
    ) -> ListResult[ResourcePoolWithSummary]:
        return await self.repository.list_with_summary(
            page=page, size=size, query=query
        )

    async def pre_delete_hook(
        self, resource_to_be_deleted: ResourcePool
    ) -> None:
        if resource_to_be_deleted.is_default():
            raise BadRequestException(
                details=[
                    BaseExceptionDetail(
                        type=CANNOT_DELETE_DEFAULT_RESOURCEPOOL_VIOLATION_TYPE,
                        message="The default resource pool cannot be deleted.",
                    )
                ]
            )

    async def post_create_hook(self, resource):
        logger.info(
            f"{AUTHZ_ADMIN}:resourcepool:created:{resource.id}",
            type=SECURITY,
        )

    async def post_update_hook(self, old_resource, updated_resource):
        logger.info(
            f"{AUTHZ_ADMIN}:resourcepool:updated:{updated_resource.id}",
            type=SECURITY,
        )

    async def post_update_many_hook(self, resources):
        resource_ids = [resource.id for resource in resources]
        logger.info(
            f"{AUTHZ_ADMIN}:resourcepools:updated:{resource_ids}",
            type=SECURITY,
        )

    async def post_delete_hook(self, resource):
        logger.info(
            f"{AUTHZ_ADMIN}:resourcepool:deleted:{resource.id}",
            type=SECURITY,
        )

    async def post_delete_many_hook(self, resources):
        resource_ids = [resource.id for resource in resources]
        logger.info(
            f"{AUTHZ_ADMIN}:resourcepools:deleted:{resource_ids}",
            type=SECURITY,
        )
