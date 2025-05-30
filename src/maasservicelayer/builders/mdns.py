# Copyright 2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from datetime import datetime
from typing import Union

from pydantic import Field
from pydantic.networks import IPvAnyAddress

from maasservicelayer.models.base import ResourceBuilder, UNSET, Unset


class MDNSBuilder(ResourceBuilder):
    """Autogenerated from utilities/generate_builders.py.

    You can still add your custom methods here, they won't be overwritten by
    the generated code.
    """

    count: Union[int, Unset] = Field(default=UNSET, required=False)
    created: Union[datetime, Unset] = Field(default=UNSET, required=False)
    hostname: Union[str, None, Unset] = Field(default=UNSET, required=False)
    interface_id: Union[int, Unset] = Field(default=UNSET, required=False)
    ip: Union[IPvAnyAddress, None, Unset] = Field(
        default=UNSET, required=False
    )
    updated: Union[datetime, Unset] = Field(default=UNSET, required=False)
