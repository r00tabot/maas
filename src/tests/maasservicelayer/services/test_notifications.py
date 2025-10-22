# Copyright 2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).
from unittest.mock import Mock

import pytest

from maascommon.enums.notifications import NotificationCategoryEnum
from maascommon.logging.security import AUTHZ_ADMIN, SECURITY
from maasservicelayer.auth.jwt import UserRole
from maasservicelayer.context import Context
from maasservicelayer.db.repositories.notifications import (
    NotificationsRepository,
)
from maasservicelayer.exceptions.catalog import (
    BadRequestException,
    NotFoundException,
)
from maasservicelayer.models.auth import AuthenticatedUser
from maasservicelayer.models.notifications import Notification
from maasservicelayer.services import notifications as notifications_module
from maasservicelayer.services.notifications import NotificationsService
from tests.fixtures import MockLoggerMixin
from tests.maasservicelayer.services.base import ServiceCommonTests

TEST_NOTIFICATION = Notification(
    id=1,
    ident="deprecation_MD5_users",
    message="Foo is deprecated, please update",
    users=True,
    admins=False,
    context={},
    user_id=None,
    category=NotificationCategoryEnum.WARNING,
    dismissable=True,
)


@pytest.mark.asyncio
class TestCommonNotificationsService(ServiceCommonTests, MockLoggerMixin):
    module = notifications_module

    @pytest.fixture
    def service_instance(self) -> NotificationsService:
        return NotificationsService(
            context=Context(), repository=Mock(NotificationsRepository)
        )

    @pytest.fixture
    def test_instance(self) -> Notification:
        return Notification(
            id=1,
            ident="deprecation_MD5_users",
            message="Foo is deprecated, please update",
            users=True,
            admins=False,
            context={},
            user_id=None,
            category=NotificationCategoryEnum.WARNING,
            dismissable=True,
        )

    async def test_post_create_hook(
        self,
        service_instance: NotificationsService,
        test_instance: Notification,
        mock_logger: Mock,
    ):
        await service_instance.post_create_hook(test_instance)
        mock_logger.info.assert_called_with(
            f"{AUTHZ_ADMIN}:notification:created:{test_instance.id}",
            type=SECURITY,
        )

    async def test_post_update_hook(
        self,
        service_instance: NotificationsService,
        test_instance: Notification,
        mock_logger: Mock,
    ):
        await service_instance.post_update_hook(test_instance, test_instance)
        mock_logger.info.assert_called_with(
            f"{AUTHZ_ADMIN}:notification:updated:{test_instance.id}",
            type=SECURITY,
        )

    async def test_post_update_many_hook(
        self,
        service_instance: NotificationsService,
        test_instance: Notification,
        mock_logger: Mock,
    ):
        await service_instance.post_update_many_hook([test_instance])
        mock_logger.info.assert_called_with(
            f"{AUTHZ_ADMIN}:notifications:updated:{[test_instance.id]}",
            type=SECURITY,
        )

    async def test_post_delete_hook(
        self,
        service_instance: NotificationsService,
        test_instance: Notification,
        mock_logger: Mock,
    ):
        await service_instance.post_delete_hook(test_instance)
        mock_logger.info.assert_called_with(
            f"{AUTHZ_ADMIN}:notification:deleted:{test_instance.id}",
            type=SECURITY,
        )

    async def test_post_delete_many_hook(
        self,
        service_instance: NotificationsService,
        test_instance: Notification,
        mock_logger: Mock,
    ):
        await service_instance.post_delete_many_hook([test_instance])
        mock_logger.info.assert_called_with(
            f"{AUTHZ_ADMIN}:notifications:deleted:{[test_instance.id]}",
            type=SECURITY,
        )


class TestNotificationsService:
    @pytest.fixture
    def notifications_repo_mock(self) -> Mock:
        return Mock(NotificationsRepository)

    @pytest.fixture
    def notifications_service(
        self, notifications_repo_mock: Mock
    ) -> NotificationsService:
        return NotificationsService(
            context=Context(), repository=notifications_repo_mock
        )

    @pytest.fixture
    def auth_user(self) -> AuthenticatedUser:
        return AuthenticatedUser(id=1, username="foo", roles={UserRole.USER})

    async def test_list_all_for_user(
        self,
        notifications_repo_mock: Mock,
        notifications_service: NotificationsService,
        auth_user: AuthenticatedUser,
    ) -> None:
        notifications_repo_mock.list_all_for_user.return_value = []
        await notifications_service.list_all_for_user(
            page=1, size=2, user=auth_user
        )
        notifications_repo_mock.list_all_for_user.assert_called_once_with(
            page=1, size=2, user_id=auth_user.id, is_admin=auth_user.is_admin()
        )

    async def test_list_active_for_user(
        self,
        notifications_repo_mock: Mock,
        notifications_service: NotificationsService,
        auth_user: AuthenticatedUser,
    ) -> None:
        notifications_repo_mock.list_active_for_user.return_value = []
        await notifications_service.list_active_for_user(
            page=1, size=2, user=auth_user
        )
        notifications_repo_mock.list_active_for_user.assert_called_once_with(
            page=1, size=2, user_id=auth_user.id, is_admin=auth_user.is_admin()
        )

    async def test_get_by_id_for_user(
        self,
        notifications_repo_mock: Mock,
        notifications_service: NotificationsService,
        auth_user: AuthenticatedUser,
    ) -> None:
        notifications_repo_mock.get_by_id_for_user.return_value = (
            TEST_NOTIFICATION
        )
        await notifications_service.get_by_id_for_user(
            notification_id=1, user=auth_user
        )
        notifications_repo_mock.get_by_id_for_user.assert_called_once_with(
            notification_id=1,
            user_id=auth_user.id,
            is_admin=auth_user.is_admin(),
        )

    async def test_dismiss(
        self,
        notifications_repo_mock: Mock,
        notifications_service: NotificationsService,
        auth_user: AuthenticatedUser,
    ) -> None:
        notifications_repo_mock.get_by_id_for_user.return_value = (
            TEST_NOTIFICATION
        )
        notifications_repo_mock.create_notification_dismissal.return_value = (
            None
        )
        await notifications_service.dismiss(notification_id=1, user=auth_user)
        notifications_repo_mock.create_notification_dismissal.assert_called_once_with(
            notification_id=1,
            user_id=auth_user.id,
        )

    async def test_dismiss_non_dismissable(
        self,
        notifications_repo_mock: Mock,
        notifications_service: NotificationsService,
        auth_user: AuthenticatedUser,
    ) -> None:
        non_dismissable_notification = TEST_NOTIFICATION
        non_dismissable_notification.dismissable = False
        notifications_repo_mock.get_by_id_for_user.return_value = (
            non_dismissable_notification
        )
        notifications_repo_mock.create_notification_dismissal.return_value = (
            None
        )
        with pytest.raises(BadRequestException):
            await notifications_service.dismiss(
                notification_id=1, user=auth_user
            )
        notifications_repo_mock.create_notification_dismissal.assert_not_called()

    async def test_dismiss_not_found(
        self,
        notifications_repo_mock: Mock,
        notifications_service: NotificationsService,
        auth_user: AuthenticatedUser,
    ) -> None:
        notifications_repo_mock.get_by_id_for_user.return_value = None
        with pytest.raises(NotFoundException):
            await notifications_service.dismiss(
                notification_id=1, user=auth_user
            )
        notifications_repo_mock.create_notification_dismissal.assert_not_called()
