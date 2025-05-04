#  Copyright 2025 Canonical Ltd.  This software is licensed under the
#  GNU Affero General Public License version 3 (see the file LICENSE).

from maasservicelayer.builders.notifications import NotificationBuilder
from maasservicelayer.context import Context
from maasservicelayer.db.repositories.notifications import (
    NotificationsRepository,
)
from maasservicelayer.models.auth import AuthenticatedUser
from maasservicelayer.models.base import ListResult
from maasservicelayer.models.notifications import Notification
from maasservicelayer.services.base import BaseService, ServiceCache


class NotificationsService(
    BaseService[Notification, NotificationsRepository, NotificationBuilder]
):
    def __init__(
        self,
        context: Context,
        repository: NotificationsRepository,
        cache: ServiceCache | None = None,
    ):
        super().__init__(context, repository, cache)

    async def list_all_for_user(
        self, page: int, size: int, user: AuthenticatedUser
    ) -> ListResult[Notification]:
        return await self.repository.list_all_for_user(
            page=page, size=size, user_id=user.id, is_admin=user.is_admin()
        )

    async def list_active_for_user(
        self, page: int, size: int, user: AuthenticatedUser
    ) -> ListResult[Notification]:
        return await self.repository.list_active_for_user(
            page=page, size=size, user_id=user.id, is_admin=user.is_admin()
        )

    async def get_by_id_for_user(
        self, notification_id: int, user: AuthenticatedUser
    ) -> Notification | None:
        return await self.repository.get_by_id_for_user(
            notification_id=notification_id,
            user_id=user.id,
            is_admin=user.is_admin(),
        )

    async def dismiss(
        self, notification_id: int, user: AuthenticatedUser
    ) -> None:
        return await self.repository.dismiss(
            notification_id=notification_id,
            user_id=user.id,
            is_admin=user.is_admin(),
        )
