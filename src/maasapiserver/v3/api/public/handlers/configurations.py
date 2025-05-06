# Copyright 2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from maasapiserver.common.api.base import Handler, handler


class ConfigurationsHandler(Handler):
    """Configurations API handler."""

    TAGS = ["Configurations"]

    @handler(
        path="/configurations/{name}",
        methods=["GET"],
        tags=TAGS,
        responses={
            200: {
                "model": ConfigurationResponse,
            },
        },
        response_model_exclude_none=True,
        status_code=200,
        dependencies=[
            Depends(check_permissions(required_roles={UserRole.USER}))
        ],
    )
    async def list_domains(
        self,
        pagination_params: PaginationParams = Depends(),  # noqa: B008
        services: ServiceCollectionV3 = Depends(services),  # noqa: B008
    ) -> Response:
        domains = await services.domains.list(
            page=pagination_params.page,
            size=pagination_params.size,
        )
        next_link = None
        if domains.has_next(pagination_params.page, pagination_params.size):
            next_link = f"{V3_API_PREFIX}/domains?{pagination_params.to_next_href_format()}"
        return DomainsListResponse(
            items=[
                DomainResponse.from_model(
                    domain=domain,
                    self_base_hyperlink=f"{V3_API_PREFIX}/domains",
                )
                for domain in domains.items
            ],
            total=domains.total,
            next=next_link,
        )

    @handler(
        path="/domains/{domain_id}",
        methods=["GET"],
        tags=TAGS,
        responses={
            200: {
                "model": DomainResponse,
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
    async def get_domain(
        self,
        domain_id: int,
        response: Response,
        services: ServiceCollectionV3 = Depends(services),  # noqa: B008
    ) -> Response:
        domain = await services.domains.get_by_id(domain_id)
        if not domain:
            return NotFoundResponse()

        response.headers["ETag"] = domain.etag()
        return DomainResponse.from_model(
            domain=domain, self_base_hyperlink=f"{V3_API_PREFIX}/domains"
        )
