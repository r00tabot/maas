#  Copyright 2025 Canonical Ltd.  This software is licensed under the
#  GNU Affero General Public License version 3 (see the file LICENSE).
from enum import StrEnum
import re
from typing import Annotated

from fastapi import Header
from pydantic import BaseModel

from maascommon.enums.boot_resources import (
    BootResourceFileType,
    BootResourceType,
)
from maascommon.osystem import OperatingSystem, OperatingSystemRegistry
from maasservicelayer.builders.bootresources import BootResourceBuilder
from maasservicelayer.db.filters import QuerySpec
from maasservicelayer.db.repositories.bootresources import (
    BootResourceClauseFactory,
)
from maasservicelayer.exceptions.catalog import ValidationException
from maasservicelayer.services import ServiceCollectionV3
from maasservicelayer.utils.date import utcnow

LINUX_OSYSTEMS = ("ubuntu", "centos", "rhel", "ol")


class BootResourceFileTypeChoice(StrEnum):
    TGZ = "tgz"
    TBZ = "tbz"
    TXZ = "txz"
    DDTGZ = "ddtgz"
    DDTBZ = "ddtbz"
    DDTXZ = "ddtxz"
    DDTAR = "ddtar"
    DDBZ2 = "ddbz2"
    DDGZ = "ddgz"
    DDXZ = "ddxz"
    DDRAW = "ddraw"

    @staticmethod
    def get_resource_filetype(
        value: "BootResourceFileTypeChoice",
    ) -> BootResourceFileType:
        """Convert the upload filetype to the filetype for `BootResource`."""
        filetypes = {
            BootResourceFileTypeChoice.TGZ: BootResourceFileType.ROOT_TGZ,
            BootResourceFileTypeChoice.TBZ: BootResourceFileType.ROOT_TBZ,
            BootResourceFileTypeChoice.TXZ: BootResourceFileType.ROOT_TXZ,
            BootResourceFileTypeChoice.DDTGZ: BootResourceFileType.ROOT_DDTGZ,
            BootResourceFileTypeChoice.DDTAR: BootResourceFileType.ROOT_DDTAR,
            BootResourceFileTypeChoice.DDRAW: BootResourceFileType.ROOT_DDRAW,
            BootResourceFileTypeChoice.DDTBZ: BootResourceFileType.ROOT_DDTBZ,
            BootResourceFileTypeChoice.DDTXZ: BootResourceFileType.ROOT_DDTXZ,
            BootResourceFileTypeChoice.DDBZ2: BootResourceFileType.ROOT_DDBZ2,
            BootResourceFileTypeChoice.DDGZ: BootResourceFileType.ROOT_DDGZ,
            BootResourceFileTypeChoice.DDXZ: BootResourceFileType.ROOT_DDXZ,
        }
        return filetypes.get(value, BootResourceFileType.ROOT_TGZ)


class BootResourceCreateRequest(BaseModel):
    name: Annotated[str, Header(description="Name of the boot resource.")]
    sha256: Annotated[
        str, Header(description="The `sha256` hash of the resource.")
    ]
    size: Annotated[
        int, Header(description="The size of the resource in bytes.")
    ]
    architecture: Annotated[
        str, Header(description="Architecture the boot resource supports.")
    ]
    file_type: Annotated[
        BootResourceFileTypeChoice,
        Header(description="Filetype for uploaded content."),
    ] = BootResourceFileTypeChoice.TGZ

    title: Annotated[
        str | None, Header(description="Title for the boot resource.")
    ]
    base_image: Annotated[
        str | None,
        Header(
            description="The Base OS image a custom image is built on top of. Only required for custom image."
        ),
    ]

    def _get_supported_operating_systems(self) -> dict[str, OperatingSystem]:
        return {os_name: os for os_name, os in OperatingSystemRegistry}

    async def _get_reserved_os_names(
        self,
        supported_osystems: list[str],
        services: ServiceCollectionV3,
    ) -> list[str]:
        # Prevent the user from uploading any <osystem>/<release> or system name already used in the SimpleStreams.
        boot_source_caches = await services.boot_source_cache.get_many(
            query=QuerySpec()
        )
        reserved_names = [
            f"{boot_source_cache.os}/{boot_source_cache.release}"
            for boot_source_cache in boot_source_caches
        ]
        reserved_names += [
            i for name in reserved_names for i in name.split("/")
        ]

        reserved_names.extend(list(supported_osystems))
        return reserved_names

    async def _validate_name(
        self, name: str, services: ServiceCollectionV3
    ) -> str:
        supported_osystems = list(
            self._get_supported_operating_systems().keys()
        )

        if "/" in name:
            osystem, release = name.split("/")
            if osystem == "custom":
                name = release
            elif osystem not in supported_osystems:
                raise ValidationException.build_for_field(
                    field="name",
                    message=f"Unsupported operating system {osystem}, supported operating systems: {supported_osystems}",
                )

        reserved_names = await self._get_reserved_os_names(
            supported_osystems, services
        )

        # Reserve CentOS version names for future MAAS use.
        if name in reserved_names or re.search(r"^centos\d\d?$", name):
            raise ValidationException.build_for_field(
                field="name",
                message=f"{name} is a reserved name",
            )
        return name

    async def _validate_architecture(
        self, architecture: str, services: ServiceCollectionV3
    ) -> str:
        architecture = architecture.lower().strip()

        if not re.match(r"([a-zA-Z0-9]+)\/([a-zA-Z0-9\.-]+)", architecture):
            raise ValidationException.build_for_field(
                field="architecture",
                message="Not a valid architecture string, needs to be in form '<arch>/<subarch>'",
            )

        all_usable_architectures = sorted(
            await services.boot_resources.get_usable_architectures()
        )
        if len(all_usable_architectures) == 0:
            return architecture
        else:
            if architecture in all_usable_architectures:
                return architecture
            else:
                raise ValidationException.build_for_field(
                    field="architecture",
                    message="Not a valid usable architecture",
                )

    async def _get_base_image_info(
        self,
        base_image: str | None,
        name: str,
        architecture: str,
        rtype: BootResourceType,
        services: ServiceCollectionV3,
    ) -> tuple[str, str]:
        if not base_image:
            existing_boot_resource = await services.boot_resources.get_one(
                query=QuerySpec(
                    where=BootResourceClauseFactory.and_clauses(
                        [
                            BootResourceClauseFactory.with_name(name),
                            BootResourceClauseFactory.with_architecture(
                                architecture
                            ),
                            BootResourceClauseFactory.with_rtype(rtype),
                        ]
                    ),
                )
            )

            # TODO: Not sure this 100% translates from V2
            if existing_boot_resource:
                base_image = existing_boot_resource.base_image
            else:
                base_image = ""

        # Will throw ValueError if `base_image` doesn't contain '/'
        # and can't unpack
        osystem, version = base_image.split("/")
        return (osystem.lower(), version.lower())

    async def _validate_base_image(
        self,
        base_image: str | None,
        name: str,
        architecture: str,
        rtype: BootResourceType,
        services: ServiceCollectionV3,
    ) -> str:
        split_name = name.split("/")
        if len(split_name) > 1 and split_name[0] != "custom":
            return ""

        base_osystem: str = ""
        base_version: str = ""
        try:
            base_osystem, base_version = await self._get_base_image_info(
                base_image, name, architecture, rtype, services
            )
        except ValueError:
            if not base_image:
                configs = await services.configurations.get_many(
                    names=set(
                        [
                            "commissioning_osystem",
                            "commissioning_distro_series",
                        ]
                    ),
                )
                vals = configs.values()
                return "/".join([val for val in vals])
            else:
                raise ValidationException.build_for_field(  # noqa: B904
                    field="base_image",
                    message="Base image must be in the format: <osystem>/<version>",
                )
        else:
            if base_osystem not in LINUX_OSYSTEMS:
                raise ValidationException.build_for_field(
                    field="base_image",
                    message="Unsupported operating system",  # TODO: Fix
                )
            if base_version is None:
                raise ValidationException.build_for_field(
                    field="base_image",
                    message="Unsupported operating system",  # TODO: Fix
                )

        supported_base_images = self._get_supported_operating_systems()
        if base_osystem not in supported_base_images and supported_base_images[
            base_osystem
        ].is_release_supported(base_version):
            raise ValidationException.build_for_field(
                field="base_image",
                message=f"Unsupported base image {base_osystem}/{base_version}",
            )

        return "/".join([base_osystem, base_version])

    async def to_builder(
        self,
        services: ServiceCollectionV3,
    ) -> BootResourceBuilder:
        now = utcnow()

        name = await self._validate_name(self.name, services)

        architecture = await self._validate_architecture(
            self.architecture, services
        )
        subarches = {"subarches": architecture.split("/")[1]}

        rtype = BootResourceType.UPLOADED

        base_image = await self._validate_base_image(
            self.base_image, name, architecture, rtype, services
        )

        extra = subarches
        if self.title:
            extra["title"] = self.title

        return BootResourceBuilder(
            alias="",
            architecture=architecture,
            base_image=base_image,
            bootloader_type=None,
            extra=subarches,
            kflavor=None,
            name=name,
            rolling=False,
            rtype=rtype,
            last_deployed=None,
            created=now,
            updated=now,
        )
