#  Copyright 2024-2025 Canonical Ltd.  This software is licensed under the
#  GNU Affero General Public License version 3 (see the file LICENSE).

from typing import Optional, Self

from pydantic import IPvAnyAddress

from maasapiserver.v3.api.public.models.responses.base import (
    BaseHal,
    BaseHref,
    HalResponse,
    PaginatedResponse,
)
from maascommon.enums.subnet import RdnsMode
from maasservicelayer.models.fields import IPv4v6Network
from maasservicelayer.models.subnets import Subnet


class SubnetResponse(HalResponse[BaseHal]):
    kind = "Subnet"
    id: int
    name: Optional[str]
    description: Optional[str]
    cidr: IPv4v6Network
    rdns_mode: RdnsMode
    gateway_ip: Optional[IPvAnyAddress]
    dns_servers: Optional[list[str]]
    allow_dns: bool
    allow_proxy: bool
    active_discovery: bool
    managed: bool
    disabled_boot_architectures: list[str]

    @classmethod
    def from_model(cls, subnet: Subnet, self_base_hyperlink: str) -> Self:
        return cls(
            id=subnet.id,
            name=subnet.name,
            description=subnet.description,
            cidr=subnet.cidr,
            rdns_mode=subnet.rdns_mode,
            gateway_ip=subnet.gateway_ip,
            dns_servers=subnet.dns_servers,
            allow_dns=subnet.allow_dns,
            allow_proxy=subnet.allow_proxy,
            active_discovery=subnet.active_discovery,
            managed=subnet.managed,
            disabled_boot_architectures=subnet.disabled_boot_architectures,
            hal_links=BaseHal(  # pyright: ignore [reportCallIssue]
                self=BaseHref(
                    href=f"{self_base_hyperlink.rstrip('/')}/{subnet.id}"
                )
            ),
        )


class SubnetsListResponse(PaginatedResponse[SubnetResponse]):
    kind = "SubnetsList"
