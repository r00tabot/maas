#  Copyright 2025 Canonical Ltd.  This software is licensed under the
#  GNU Affero General Public License version 3 (see the file LICENSE).
from contextlib import suppress
from typing import Any, Type, TypeVar

from deprecated import deprecated
import structlog

from maascommon.enums.events import EventTypeEnum
from maasservicelayer.builders.events import EventBuilder
from maasservicelayer.context import Context
from maasservicelayer.db.filters import QuerySpec
from maasservicelayer.db.repositories.database_configurations import (
    DatabaseConfigurationNotFound,
    DatabaseConfigurationsClauseFactory,
)
from maasservicelayer.models.configurations import Config, ConfigFactory
from maasservicelayer.models.events import EventType
from maasservicelayer.services import (
    SecretsService, EventsService,
)
from maasservicelayer.services.base import Service
from maasservicelayer.services.database_configurations import DatabaseConfigurationsService
from maasservicelayer.services.secrets import SecretNotFound

T = TypeVar("T", bound=Config)


class ConfigurationsService(Service):
    def __init__(
        self,
        context: Context,
        database_configurations_service: DatabaseConfigurationsService,
        secrets_service: SecretsService,
        events_service: EventsService
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
                return await self.secrets_service.get_simple_secret(
                    config_model.secret_name
                )
            return self.database_configurations_service.get(name=name)
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
                    configs[name] = await self.secrets_service.get_simple_secret(
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

    async def set(self, name: str, value: Any, user=None):
        """Set or overwrite a config value.

        :param name: The name of the config item to set.
        :type name: unicode
        :param value: The value of the config item to set.
        :type value: Any jsonizable object
        :param endpoint: The endpoint of the audit event to be created.
        :type endpoint: Integer enumeration of ENDPOINT.
        :param request: The http request of the audit event to be created.
        :type request: HttpRequest object.
        """
        config_model = None
        try:
            config_model = ConfigFactory.get_config_model(name)
        except ValueError:
            structlog.warn(
                f"The configuration '{name}' is not known. Anyways, it's going to be stored in the DB."
            )
        if config_model and config_model.stored_as_secret:
            await self.secrets_service.set_simple_secret(
                config_model.secret_name, value
            )
        else:
            self.update_or_create(name=name, defaults={"value": value})
        structlog.info(f"Configuration '{name}' has been updated.")

        # TODO CLEAR SESSIONS

        await self.events_service.record_event(
            event_type=EventTypeEnum.SETTINGS,
            event_description=f"Updated configuration setting '{name}' to '{value}'.",
            user=user,
        )
