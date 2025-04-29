# Copyright 2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from typing import Any, Optional

from fastapi import Query
from pydantic import BaseModel, Field, IPvAnyAddress, root_validator

from maasservicelayer.exceptions.catalog import ValidationException
from maasservicelayer.models.fields import MacAddress


class DiscoveriesIPAndMacFiltersParams(BaseModel):
    ip: Optional[IPvAnyAddress] = Field(
        Query(default=None, description="Delete discoveries with this IP.")
    )
    mac: Optional[MacAddress] = Field(
        Query(default=None, description="Delete discoveries with this MAC.")
    )

    # TODO: switch to model_validator when we migrate to pydantic 2.x
    @root_validator
    def validate_model(cls, values: dict[str, Any]):
        if values["ip"] is not None:
            if values["mac"] is None:
                raise ValidationException.build_for_field(
                    "mac",
                    "Missing MAC address. You have to specify both the IP and the MAC.",
                )

        if values["mac"] is not None:
            if values["ip"] is None:
                raise ValidationException.build_for_field(
                    "ip",
                    "Missing IP address. You have to specify both the IP and the MAC.",
                )
        return values
