#  Copyright 2026 Canonical Ltd.  This software is licensed under the
#  GNU Affero General Public License version 3 (see the file LICENSE).
from django.contrib.auth.models import User
from django.db import connection

from maascommon.openfga.client.sync import SyncOpenFGAClient


class OpenFGAClientMock(SyncOpenFGAClient):
    # Mock openfga using the following policy:
    # - If the user is a superuser, they can do everything.
    # - If the user is not a superuser, they can view everything but not edit anything.

    def __init__(self):
        super().__init__()

    def _get_resource_pools(self) -> list[str]:
        with connection.cursor() as cursor:
            # Hack to tell maastesting.djangotestcase.CountQueries to not count this query
            cursor.execute(
                "SELECT id FROM maasserver_resourcepool; /* COUNTQUERIES-IGNOREME */"
            )
            result = cursor.fetchall()
            return [str(row[0]) for row in result]

    def can_edit_machines(self, user: User) -> bool:
        if user.is_superuser:
            return True
        return False

    def can_edit_machines_in_pool(self, user: User, pool_id: str) -> bool:
        if user.is_superuser:
            return True
        return False

    def can_deploy_machines_in_pool(self, user: User, pool_id: str) -> bool:
        return True

    def can_view_machines_in_pool(self, user: User, pool_id: str) -> bool:
        if user.is_superuser:
            return True
        return False

    def can_view_available_machines_in_pool(
        self, user: User, pool_id: str
    ) -> bool:
        return True

    def can_view_global_entities(self, user: User) -> bool:
        return True

    def can_edit_global_entities(self, user: User) -> bool:
        if user.is_superuser:
            return True
        return False

    def can_view_controllers(self, user: User) -> bool:
        if user.is_superuser:
            return True
        return False

    def can_edit_controllers(self, user: User) -> bool:
        if user.is_superuser:
            return True
        return False

    def can_view_permissions(self, user: User) -> bool:
        if user.is_superuser:
            return True
        return False

    def can_edit_permissions(self, user: User) -> bool:
        if user.is_superuser:
            return True
        return False

    def can_view_configurations(self, user: User) -> bool:
        if user.is_superuser:
            return True
        return False

    def can_edit_configurations(self, user: User) -> bool:
        if user.is_superuser:
            return True
        return False

    def can_edit_notifications(self, user: User):
        if user.is_superuser:
            return True
        return False

    def can_view_notifications(self, user: User):
        if user.is_superuser:
            return True
        return False

    def can_view_devices(self, user: User):
        if user.is_superuser:
            return True
        return False

    def can_view_ipaddresses(self, user: User):
        if user.is_superuser:
            return True
        return False

    def list_pools_with_view_machines_access(self, user: User) -> list[str]:
        return []

    def list_pools_with_view_deployable_machines_access(
        self, user: User
    ) -> list[str]:
        return self._get_resource_pools()

    def list_pool_with_deploy_machines_access(self, user: User) -> list[str]:
        return self._get_resource_pools()

    def list_pools_with_edit_machines_access(self, user: User) -> list[str]:
        if user.is_superuser:
            return self._get_resource_pools()
        else:
            return []
