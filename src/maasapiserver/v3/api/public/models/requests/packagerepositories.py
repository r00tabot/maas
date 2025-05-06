# Copyright 2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from typing import Any

from pydantic import BaseModel, Field, root_validator

from maascommon.enums.package_repositories import (
    ComponentsToDisableEnum,
    KnownArchesEnum,
    KnownComponentsEnum,
    MainArchesEnum,
    PocketsToDisableEnum,
    PortsArchesEnum,
)
from maasservicelayer.builders.packagerepositories import (
    PackageRepositoryBuilder,
)
from maasservicelayer.exceptions.catalog import ValidationException
from maasservicelayer.models.fields import PackageRepoUrl


class PackageRepositoryCreateRequest(BaseModel):
    name: str = Field(description="The name of the package repository.")
    key: str | None = Field(
        description="The authentication key to use with the repository.",
        default="",
    )
    url: PackageRepoUrl = Field(
        description="The url of the package repository."
    )
    distributions: list[str] = Field(
        description="Which package distribution to include.",
        default_factory=list,
    )
    components: set[KnownComponentsEnum] = Field(
        description="The list of components to enable."
        "Only applicable to custom repositories.",
        default_factory=set,
    )
    arches: set[KnownArchesEnum] = Field(
        description="The list of supported architectures.",
        default_factory=set,
    )
    disabled_pockets: set[PocketsToDisableEnum] = Field(
        description="The list of pockets to disable.",
        default_factory=set,
    )
    disabled_components: set[ComponentsToDisableEnum] = Field(
        description="The list of components to disable."
        "Only applicable to the default Ubuntu repositories.",
        default_factory=set,
    )
    disable_sources: bool = Field(description="Disable deb-src lines.")
    enabled: bool = Field(
        description="Whether or not the repository is enabled.", default=True
    )

    @root_validator
    def populate_arches_if_empty(cls, values: dict[str, Any]):
        if len(values["arches"]) == 0:
            if values["name"] == "ports_archive":
                values["arches"] = set(PortsArchesEnum.__members__)
            else:
                values["arches"] = set(MainArchesEnum.__members__)
        return values

    @classmethod
    def to_builder(cls, is_default: bool = False) -> PackageRepositoryBuilder:
        return PackageRepositoryBuilder(
            name=cls.name,
            key=cls.key,
            url=cls.url,
            distributions=cls.distributions,
            components=cls.components,
            arches=cls.arches,
            disabled_pockets=cls.disabled_pockets,
            disabled_components=cls.disabled_components,
            disable_sources=cls.disable_sources,
            enabled=cls.enabled,
        )


class PackageRepositoryUpdateRequest(PackageRepositoryCreateRequest):
    @classmethod
    def to_builder(cls, is_default: bool = False) -> PackageRepositoryBuilder:
        if is_default and not cls.enabled:
            raise ValidationException.build_for_field(
                field="enabled",
                message="Default repositories may not be disabled.",
            )
        return super().to_builder()
