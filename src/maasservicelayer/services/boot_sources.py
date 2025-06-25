# Copyright 2025 Canonical Ltd. This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import asyncio
import os

from simplestreams.mirrors import UrlMirrorReader
from simplestreams.util import path_from_mirror_url
import structlog

from maascommon.utils.fs import tempdir
from maasservicelayer.context import Context
from maasservicelayer.services.base import Service
from maasservicelayer.services.configurations import ConfigurationsService
from maasservicelayer.utils.images.boot_image_mapping import BootImageMapping
from maasservicelayer.utils.images.helpers import get_signing_policy
from maasservicelayer.utils.images.keyrings import (
    calculate_keyring_name,
    write_keyring,
)
from maasservicelayer.utils.images.repo_dumper import RepoDumper

logger = structlog.getLogger()


class BootSourcesService(Service):
    def __init__(
        self,
        context: Context,
        configuration_service: ConfigurationsService,
    ) -> None:
        super().__init__(context)
        self.configuration_service = configuration_service

    async def fetch(
        self,
        source_url: str,
        keyring_path: str | None = None,
        keyring_data: str | None = None,
        validate_products: bool = True,
    ) -> BootImageMapping:
        """Download image metadata from upstream Simplestreams repo.

        :param source_url: The path to a Simplestreams repo.
        :param keyring_path: Optional filepath to the keyring for verifying the repo's signatures.
        :param keyring_data: Optional keyring data for verifying the repo's signatures.
        :param validate_products: Whether to validate products in the boot
            sources.
        :return: A `BootImageMapping` describing available boot resources.
        """
        user_agent = await self.configuration_service.get_maas_user_agent()
        return await asyncio.to_thread(
            self._fetch,
            source_url,
            user_agent,
            keyring_path,
            keyring_data,
            validate_products,
        )

    def _fetch(
        self,
        source_url: str,
        user_agent: str,
        keyring_path: str | None = None,
        keyring_data: str | None = None,
        validate_products: bool = True,
    ) -> BootImageMapping:
        logger.info(f"Downloading image descriptions from '{source_url}'.")
        mirror, rpath = path_from_mirror_url(source_url, None)

        # The simplestreams library uses an optional path to the keyring file,
        # but we want to allow the user to provide a keyring file path or the
        # keyring data directly.

        # If both of the keyring parameters are provided, ignore keyring_data.
        # The V3 API request has a validator to stop both being provided, but
        # the V2 API doesn't, so need a fallback.
        if keyring_path is not None and keyring_data is not None:
            logger.warning(
                "Both a keyring file and keyring data were specified; ignoring keyring_data."
            )
        elif keyring_data is not None:
            # Otherwise, write the keyring data to a temporary file and use the
            # path to that temporary file for keyring_path
            with tempdir("keyrings") as keyrings_path:
                keyring_path = os.path.join(
                    keyrings_path, calculate_keyring_name(source_url)
                )
                write_keyring(keyring_path, keyring_data.encode("utf8"))

        policy = get_signing_policy(rpath, keyring_path)

        try:
            reader = UrlMirrorReader(
                mirror, policy=policy, user_agent=user_agent
            )
        except TypeError:
            # UrlMirrorReader doesn't support the user_agent argument.
            # simplestream >=bzr429 is required for this feature.
            reader = UrlMirrorReader(mirror, policy=policy)

        boot_images_dict = BootImageMapping()
        dumper = RepoDumper(
            boot_images_dict, validate_products=validate_products
        )
        dumper.sync(reader, rpath)
        return boot_images_dict
