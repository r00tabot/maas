#  Copyright 2024-2025 Canonical Ltd.  This software is licensed under the
#  GNU Affero General Public License version 3 (see the file LICENSE).

from typing import Optional, Self

from maasapiserver.v3.api.public.models.responses.base import (
    BaseHal,
    BaseHref,
    HalResponse,
    PaginatedResponse,
)
from maasapiserver.v3.constants import V3_API_PREFIX
from maasservicelayer.models.spaces import Space


class SpaceResponse(HalResponse[BaseHal]):
    kind = "Space"
    id: int
    name: Optional[str]
    description: Optional[str]
    vlans: BaseHref
    subnets: BaseHref

    @classmethod
    def from_model(cls, space: Space, self_base_hyperlink: str) -> Self:
        return cls(
            id=space.id,
            name=space.name,
            description=space.description,
            vlans=BaseHref(
                href=f"{V3_API_PREFIX}/vlans?filter=space_id eq {space.id}"
            ),
            subnets=BaseHref(
                href=f"{V3_API_PREFIX}/subnets?filter=space_id eq {space.id}"
            ),
            hal_links=BaseHal(  # pyright: ignore [reportCallIssue]
                self=BaseHref(
                    href=f"{self_base_hyperlink.rstrip('/')}/{space.id}"
                )
            ),
        )


class SpacesListResponse(PaginatedResponse[SpaceResponse]):
    kind = "SpacesList"
