# Copyright 2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from datetime import datetime
from typing import Union

from pydantic import Field

from maascommon.enums.boot_resources import BootResourceType
from maasservicelayer.models.base import ResourceBuilder, UNSET, Unset


class BootResourceBuilder(ResourceBuilder):
    """Autogenerated from utilities/generate_builders.py.

    You can still add your custom methods here, they won't be overwritten by
    the generated code.
    """

    alias: Union[str, None, Unset] = Field(default=UNSET, required=False)
    architecture: Union[str, Unset] = Field(default=UNSET, required=False)
    base_image: Union[str, Unset] = Field(default=UNSET, required=False)
    bootloader_type: Union[str, None, Unset] = Field(
        default=UNSET, required=False
    )
    created: Union[datetime, Unset] = Field(default=UNSET, required=False)
    extra: Union[dict, Unset] = Field(default=UNSET, required=False)
    kflavor: Union[str, None, Unset] = Field(default=UNSET, required=False)
    last_deployed: Union[datetime, None, Unset] = Field(
        default=UNSET, required=False
    )
    name: Union[str, Unset] = Field(default=UNSET, required=False)
    rolling: Union[bool, Unset] = Field(default=UNSET, required=False)
    rtype: Union[BootResourceType, Unset] = Field(
        default=UNSET, required=False
    )
    updated: Union[datetime, Unset] = Field(default=UNSET, required=False)
