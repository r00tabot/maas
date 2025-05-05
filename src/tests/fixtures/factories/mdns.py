# Copyright 2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).


from typing import Any

from maasservicelayer.models.mdns import MDNS
from maasservicelayer.utils.date import utcnow
from tests.maasapiserver.fixtures.db import Fixture


async def create_test_mdns_entry(
    fixture: Fixture,
    hostname: str,
    ip: str,
    interface_id: int,
    **extra_details: Any,
) -> MDNS:
    now = utcnow()
    mdns = {
        "hostname": hostname,
        "ip": ip,
        "interface_id": interface_id,
        "created": now,
        "updated": now,
        "count": 1,
    }
    mdns.update(extra_details)

    [created_mdns] = await fixture.create("maasserver_mdns", [mdns])
    return MDNS(**created_mdns)
