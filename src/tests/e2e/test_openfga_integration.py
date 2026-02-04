# Copyright 2026 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from datetime import timedelta
import os
import subprocess
import time

import pytest
import yaml

from maascommon.openfga.client.client import OpenFGAClient
from maasservicelayer.builders.openfga_tuple import OpenFGATupleBuilder
from maasservicelayer.context import Context
from maasservicelayer.services import CacheForServices, ServiceCollectionV3


@pytest.fixture
def project_root_path(request):
    return request.config.rootpath


@pytest.fixture
def openfga_socket_path(tmpdir):
    return tmpdir / "openfga-http.sock"


@pytest.fixture
def openfga_server(tmpdir, project_root_path, openfga_socket_path, db):
    """Fixture to start the OpenFGA server as a subprocess for testing. After the test is done, it ensures that the server process is terminated."""
    binary_path = project_root_path / "src/maasopenfga/build/maas-openfga"

    # Set the environment variable for the OpenFGA server to use the socket path in the temporary directory
    env = os.environ.copy()
    env["MAAS_OPENFGA_HTTP_SOCKET_PATH"] = str(openfga_socket_path)

    regiond_conf = {
        "database_host": db.config.host,
        "database_name": db.config.name,
        "database_user": "ubuntu",
    }

    # Write the regiond configuration to a file in the temporary directory
    with open(tmpdir / "regiond.conf", "w") as f:
        f.write(yaml.dump(regiond_conf))

    env["SNAP_DATA"] = str(tmpdir)

    pid = subprocess.Popen(binary_path, env=env)

    timeout = timedelta(seconds=30)
    start_time = time.monotonic()
    while True:
        if time.monotonic() - start_time > timeout.total_seconds():
            pid.terminate()
            raise TimeoutError(
                "OpenFGA server did not start within the expected time."
            )
        if not openfga_socket_path.exists():
            time.sleep(0.5)
        else:
            break
    yield pid
    pid.terminate()


@pytest.mark.asyncio
class TestIntegrationConfigurationsService:
    @pytest.mark.allow_transactions
    @pytest.mark.usefixtures("db_connection")
    async def test_get(
        self, openfga_server, openfga_socket_path, db_connection, db
    ):
        services = await ServiceCollectionV3.produce(
            Context(connection=db_connection), cache=CacheForServices()
        )

        # team A has system rights
        await services.openfga_tuples.create(
            OpenFGATupleBuilder.build_group_system_tuple(group_id="teamA")
        )

        # system groups can manage pool1
        await services.openfga_tuples.create(
            OpenFGATupleBuilder.build_system_controls_pool_tuple(
                pool_id="pool1"
            )
        )

        # pippo belongs to group team A
        await services.openfga_tuples.create(
            OpenFGATupleBuilder.build_user_is_group_member_tuple(
                user_id="pippo", group_id="teamA"
            )
        )

        # pluto belongs to group team B
        await services.openfga_tuples.create(
            OpenFGATupleBuilder.build_user_is_group_member_tuple(
                user_id="pluto", group_id="teamB"
            )
        )

        # team B has pool 1 auditor rights
        await services.openfga_tuples.create(
            OpenFGATupleBuilder.build_group_is_pool_auditor_tuple(
                group_id="teamB", pool_id="pool1"
            )
        )

        # paperino is an operator on pool1
        await services.openfga_tuples.create(
            OpenFGATupleBuilder.build_user_is_pool_operator_tuple(
                user_id="pluto", pool_id="pool1"
            )
        )

        await db_connection.commit()

        client = OpenFGAClient(str(openfga_socket_path))
        # pippo should have all permissions on pool1 because of teamA's system rights
        assert (
            await client.can_user_edit_pool(user_id="pippo", pool_id="pool1")
        ) is True
        assert (
            await client.can_user_remove_machines_from_pool(
                user_id="pippo", pool_id="pool1"
            )
        ) is True
        assert (
            await client.can_user_view_machines_in_pool(
                user_id="pippo", pool_id="pool1"
            )
        ) is True
        assert (
            await client.can_user_manage_machines_in_pool(
                user_id="pippo", pool_id="pool1"
            )
        ) is True
        assert (await client.can_user_create_pools(user_id="pippo")) is True
        assert (
            await client.can_user_remove_machines_from_pool(
                user_id="pippo", pool_id="pool1"
            )
        ) is True

        # pluto should have view permissions on pool1 because of teamB's auditor rights, but not edit permissions. He should also have operator permissions because of his user-to-pool operator relationship.
        assert (
            await client.can_user_edit_pool(user_id="pluto", pool_id="pool1")
        ) is False
        assert (
            await client.can_user_delete_pool(user_id="pluto", pool_id="pool1")
        ) is False
        assert (
            await client.can_user_add_machines_to_pool(
                user_id="pluto", pool_id="pool1"
            )
        ) is False
        assert (
            await client.can_user_remove_machines_from_pool(
                user_id="pluto", pool_id="pool1"
            )
        ) is False
        assert (
            await client.can_user_deploy_machines_in_pool(
                user_id="pluto", pool_id="pool1"
            )
        ) is False
        assert (
            await client.can_user_view_machines_in_pool(
                user_id="pluto", pool_id="pool1"
            )
        ) is True
        assert (
            await client.can_user_manage_machines_in_pool(
                user_id="pluto", pool_id="pool1"
            )
        ) is False

        # paperino should have operator permissions on pool1 because of his user-to-pool operator relationship, but not admin permissions.
        assert (
            await client.can_user_edit_pool(
                user_id="paperino", pool_id="pool1"
            )
        ) is False
        assert (
            await client.can_user_delete_pool(
                user_id="paperino", pool_id="pool1"
            )
        ) is False
        assert (
            await client.can_user_add_machines_to_pool(
                user_id="paperino", pool_id="pool1"
            )
        ) is False
        assert (
            await client.can_user_remove_machines_from_pool(
                user_id="paperino", pool_id="pool1"
            )
        ) is False
        assert (
            await client.can_user_view_machines_in_pool(
                user_id="paperino", pool_id="pool1"
            )
        ) is True
        assert (
            await client.can_user_deploy_machines_in_pool(
                user_id="paperino", pool_id="pool1"
            )
        ) is True
        assert (
            await client.can_user_manage_machines_in_pool(
                user_id="paperino", pool_id="pool1"
            )
        ) is True
