# Copyright 2026 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import os
from pathlib import Path

import httpx

from maascommon.enums.openfga import (
    OPENFGA_AUTHORIZATION_MODEL_ID,
    OPENFGA_STORE_ID,
)
from maascommon.path import get_maas_data_path


class OpenFGAClient:
    """Client for interacting with OpenFGA API."""

    HEADERS = {"User-Agent": "maas-openfga-client/1.0"}

    def __init__(self, unix_socket: str | None = None):
        self.client = self._create_client(unix_socket)

    def _create_client(
        self, unix_socket: str | None = None
    ) -> httpx.AsyncClient:
        if unix_socket is None:
            unix_socket = str(self._openfga_service_socket_path())

        return httpx.AsyncClient(
            timeout=httpx.Timeout(10),
            headers=self.HEADERS,
            base_url="http://unix/",
            transport=httpx.AsyncHTTPTransport(uds=unix_socket),
        )

    def _openfga_service_socket_path(self) -> Path:
        """Return the path of the socket for the service."""
        return Path(
            os.getenv(
                "MAAS_OPENFGA_HTTP_SOCKET_PATH",
                get_maas_data_path("openfga-http.sock"),
            )
        )

    async def _check(self, tuple_key: dict):
        response = await self.client.post(
            f"/stores/{OPENFGA_STORE_ID}/check",
            json={
                "tuple_key": tuple_key,
                "authorization_model_id": OPENFGA_AUTHORIZATION_MODEL_ID,
            },
        )
        response.raise_for_status()
        data = response.json()
        return data.get("allowed", False)

    async def can_user_create_pools(self, user_id: str):
        tuple_key = {
            "user": f"user:{user_id}",
            "relation": "pools.create",
            "object": "system:system",
        }
        return await self._check(tuple_key)

    async def can_user_delete_pool(self, user_id: str, pool_id: str):
        tuple_key = {
            "user": f"user:{user_id}",
            "relation": "pool.delete",
            "object": f"pool:{pool_id}",
        }
        return await self._check(tuple_key)

    async def can_user_edit_pool(self, user_id: str, pool_id: str):
        tuple_key = {
            "user": f"user:{user_id}",
            "relation": "pool.edit",
            "object": f"pool:{pool_id}",
        }
        return await self._check(tuple_key)

    async def can_user_add_machines_to_pool(self, user_id: str, pool_id: str):
        tuple_key = {
            "user": f"user:{user_id}",
            "relation": "pool.machines.add",
            "object": f"pool:{pool_id}",
        }
        return await self._check(tuple_key)

    async def can_user_remove_machines_from_pool(
        self, user_id: str, pool_id: str
    ):
        tuple_key = {
            "user": f"user:{user_id}",
            "relation": "pool.machines.remove",
            "object": f"pool:{pool_id}",
        }
        return await self._check(tuple_key)

    async def can_user_view_machines_in_pool(self, user_id: str, pool_id: str):
        tuple_key = {
            "user": f"user:{user_id}",
            "relation": "pool.machines.view",
            "object": f"pool:{pool_id}",
        }
        return await self._check(tuple_key)

    async def can_user_deploy_machines_in_pool(
        self, user_id: str, pool_id: str
    ):
        tuple_key = {
            "user": f"user:{user_id}",
            "relation": "pool.machines.deploy",
            "object": f"pool:{pool_id}",
        }
        return await self._check(tuple_key)

    async def can_user_manage_machines_in_pool(
        self, user_id: str, pool_id: str
    ):
        tuple_key = {
            "user": f"user:{user_id}",
            "relation": "pool.machines.manage",
            "object": f"pool:{pool_id}",
        }
        return await self._check(tuple_key)
