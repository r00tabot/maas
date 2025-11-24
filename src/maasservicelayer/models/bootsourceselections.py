# Copyright 2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from maasservicelayer.models.base import (
    generate_builder,
    MaasBaseModel,
    MaasTimestampedBaseModel,
)


class BootSourceSelectionStatus(MaasBaseModel):
    id: int
    status: str
    update_status: str
    sync_percentage: float


@generate_builder()
class BootSourceSelection(MaasTimestampedBaseModel):
    os: str
    release: str
    arch: str
    boot_source_id: int
