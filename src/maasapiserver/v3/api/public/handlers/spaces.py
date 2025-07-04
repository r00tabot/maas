# Copyright 2024-2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from typing import Union

from fastapi import Depends, Header, Response
from starlette import status

from maasapiserver.common.api.base import Handler, handler
from maasapiserver.common.api.models.responses.errors import (
    BadRequestBodyResponse,
    ConflictBodyResponse,
    NotFoundBodyResponse,
)
from maasapiserver.v3.api import services
from maasapiserver.v3.api.public.models.requests.query import PaginationParams
from maasapiserver.v3.api.public.models.requests.spaces import SpaceRequest
from maasapiserver.v3.api.public.models.responses.base import (
    OPENAPI_ETAG_HEADER,
)
from maasapiserver.v3.api.public.models.responses.spaces import (
    SpaceResponse,
    SpacesListResponse,
)
from maasapiserver.v3.auth.base import check_permissions
from maasapiserver.v3.constants import V3_API_PREFIX
from maasservicelayer.auth.jwt import UserRole
from maasservicelayer.exceptions.catalog import NotFoundException
from maasservicelayer.services import ServiceCollectionV3


class SpacesHandler(Handler):
    """Spaces API handler."""

    TAGS = ["Spaces"]

    @handler(
        path="/spaces",
        methods=["GET"],
        tags=TAGS,
        responses={
            200: {"model": SpacesListResponse},
        },
        response_model_exclude_none=True,
        status_code=200,
        dependencies=[
            Depends(check_permissions(required_roles={UserRole.USER}))
        ],
    )
    async def list_spaces(
        self,
        pagination_params: PaginationParams = Depends(),  # noqa: B008
        services: ServiceCollectionV3 = Depends(services),  # noqa: B008
    ) -> SpacesListResponse:
        spaces = await services.spaces.list(
            page=pagination_params.page,
            size=pagination_params.size,
        )
        return SpacesListResponse(
            items=[
                SpaceResponse.from_model(
                    space=space, self_base_hyperlink=f"{V3_API_PREFIX}/spaces"
                )
                for space in spaces.items
            ],
            total=spaces.total,
            next=(
                f"{V3_API_PREFIX}/spaces?"
                f"{pagination_params.to_next_href_format()}"
                if spaces.has_next(
                    pagination_params.page, pagination_params.size
                )
                else None
            ),
        )

    @handler(
        path="/spaces/{space_id}",
        methods=["GET"],
        tags=TAGS,
        responses={
            200: {
                "model": SpaceResponse,
                "headers": {"ETag": OPENAPI_ETAG_HEADER},
            },
            404: {"model": NotFoundBodyResponse},
        },
        response_model_exclude_none=True,
        status_code=200,
        dependencies=[
            Depends(check_permissions(required_roles={UserRole.USER}))
        ],
    )
    async def get_space(
        self,
        space_id: int,
        response: Response,
        services: ServiceCollectionV3 = Depends(services),  # noqa: B008
    ) -> SpaceResponse:
        space = await services.spaces.get_by_id(space_id)
        if not space:
            raise NotFoundException()

        response.headers["ETag"] = space.etag()
        return SpaceResponse.from_model(
            space=space, self_base_hyperlink=f"{V3_API_PREFIX}/spaces"
        )

    @handler(
        path="/spaces",
        methods=["POST"],
        tags=TAGS,
        responses={
            201: {
                "model": SpaceResponse,
                "headers": {"ETag": OPENAPI_ETAG_HEADER},
            },
            409: {"model": ConflictBodyResponse},
        },
        response_model_exclude_none=True,
        status_code=201,
        dependencies=[
            Depends(check_permissions(required_roles={UserRole.ADMIN}))
        ],
    )
    async def create_space(
        self,
        response: Response,
        space_request: SpaceRequest,
        services: ServiceCollectionV3 = Depends(services),  # noqa: B008
    ) -> SpaceResponse:
        space = await services.spaces.create(
            builder=space_request.to_builder()
        )
        response.headers["ETag"] = space.etag()
        return SpaceResponse.from_model(
            space=space, self_base_hyperlink=f"{V3_API_PREFIX}/spaces"
        )

    @handler(
        path="/spaces/{space_id}",
        methods=["PUT"],
        tags=TAGS,
        responses={
            200: {
                "model": SpaceResponse,
                "headers": {"ETag": OPENAPI_ETAG_HEADER},
            },
            404: {"model": NotFoundBodyResponse},
        },
        response_model_exclude_none=True,
        status_code=200,
        dependencies=[
            Depends(check_permissions(required_roles={UserRole.ADMIN}))
        ],
    )
    async def update_space(
        self,
        space_id: int,
        space_request: SpaceRequest,
        response: Response,
        services: ServiceCollectionV3 = Depends(services),  # noqa: B008
    ) -> SpaceResponse:
        space = await services.spaces.update_by_id(
            id=space_id,
            builder=space_request.to_builder(),
        )

        response.headers["ETag"] = space.etag()
        return SpaceResponse.from_model(
            space=space, self_base_hyperlink=f"{V3_API_PREFIX}/spaces"
        )

    @handler(
        path="/spaces/{space_id}",
        methods=["DELETE"],
        tags=TAGS,
        responses={
            204: {},
            400: {"model": BadRequestBodyResponse},
            404: {"model": NotFoundBodyResponse},
        },
        status_code=204,
        dependencies=[
            Depends(check_permissions(required_roles={UserRole.ADMIN}))
        ],
    )
    async def delete_space(
        self,
        space_id: int,
        etag_if_match: Union[str, None] = Header(
            alias="if-match", default=None
        ),
        services: ServiceCollectionV3 = Depends(services),  # noqa: B008
    ) -> Response:
        await services.spaces.delete_by_id(
            id=space_id, etag_if_match=etag_if_match
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
