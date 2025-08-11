# Copyright 2024-2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from unittest.mock import Mock

import pytest

from maasservicelayer.services import ServiceCollectionV3
from maastesting.pytest.database import ensuremaasdb, templatemaasdb

from ..maasapiserver.fixtures.db import db, db_connection, fixture, test_config

__all__ = [
    "db",
    "db_connection",
    "ensuremaasdb",
    "fixture",
    "templatemaasdb",
    "test_config",
]


@pytest.fixture
def services_mock():
    yield Mock(ServiceCollectionV3)
