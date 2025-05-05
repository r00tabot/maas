#  Copyright 2025 Canonical Ltd.  This software is licensed under the
#  GNU Affero General Public License version 3 (see the file LICENSE).
from contextlib import suppress
from typing import Any, TypeVar

import structlog

from maasservicelayer.context import Context
from maasservicelayer.db.filters import QuerySpec
from maasservicelayer.db.repositories.database_configurations import (
    DatabaseConfigurationsClauseFactory,
)
from maasservicelayer.models.configurations import Config, ConfigFactory
from maasservicelayer.services.base import Service
from maasservicelayer.services.database_configurations import (
    DatabaseConfigurationNotFound,
    DatabaseConfigurationsService,
)
from maasservicelayer.services.events import EventsService
from maasservicelayer.services.secrets import SecretNotFound, SecretsService

T = TypeVar("T", bound=Config)


class ConfigurationsService(Service):
    def __init__(
        self,
        context: Context,
        database_configurations_service: DatabaseConfigurationsService,
        secrets_service: SecretsService,
        events_service: EventsService,
    ):
        super().__init__(context)
        self.database_configurations_service = database_configurations_service
        self.secrets_service = secrets_service
        self.events_service = events_service

    async def get(self, name: str, default=None) -> Any:
        """Return the config value corresponding to the given config name.
        Return None or the provided default if the config value does not
        exist.

        :param name: The name of the config item.
        :type name: unicode
        :param default: The optional default value to return if no such config
            item exists.
        :type default: object
        :return: A config value.
        :raises: Config.MultipleObjectsReturned
        """
        config_model = None
        try:
            config_model = ConfigFactory.get_config_model(name)
        except ValueError:
            structlog.warn(
                f"The configuration '{name}' is not known. Using the default {default} if the config does not exist in the DB."
            )
            default_value = default
        else:
            default_value = config_model.default
        try:
            if config_model and config_model.stored_as_secret:
                assert config_model.secret_name is not None
                return await self.secrets_service.get_simple_secret(
                    config_model.secret_name
                )
            return await self.database_configurations_service.get(name=name)
        except (DatabaseConfigurationNotFound, SecretNotFound):
            return default_value

    async def get_many(self, names: set[str]) -> dict[str, Any]:
        """Return the config values corresponding to the given config names.
        Return None or the provided default if the config value does not
        exist.
        """

        config_models = {
            name: ConfigFactory.get_config_model(name)
            for name in names
            if name in ConfigFactory.ALL_CONFIGS
        }

        # Build a first result with all the default values, then look in the secrets/configs in the db for overrides.
        configs = {
            name: config_model.default
            for name, config_model in config_models.items()
        }

        # What configs we should lookup from the DB
        regular_configs = set(names)

        # secrets configs
        for name, model in config_models.items():
            if model.stored_as_secret:
                with suppress(SecretNotFound):
                    assert model.secret_name is not None
                    configs[
                        name
                    ] = await self.secrets_service.get_simple_secret(
                        model.secret_name
                    )
                    # The config was found and added to the result: remove it from the regular config.
                    regular_configs.remove(name)

        # Lookup the remaining configs from the DB.
        configs.update(
            await self.database_configurations_service.get_many(
                query=QuerySpec(
                    DatabaseConfigurationsClauseFactory.with_names(
                        regular_configs
                    )
                )
            )
        )
        return configs
