# Copyright 2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from typing import Any

from pydantic import BaseModel, root_validator

from maascommon.enums.notifications import NotificationCategoryEnum
from maasservicelayer.builders.notifications import NotificationBuilder


class NotificationRequest(BaseModel):
    message: str
    category: NotificationCategoryEnum = NotificationCategoryEnum.INFO
    ident: str | None
    user_id: int | None
    for_users: bool = False
    for_admins: bool = False
    context: dict = {}
    dismissable: bool = True

    @root_validator
    def validate_recipient(cls, values: dict[str, Any]):
        if (
            values["user_id"] is None
            and values["for_users"] is False
            and values["for_admins"] is False
        ):
            raise ValueError(
                "Either 'user_id', 'for_users' or 'for_admin' must be specified."
            )
        return values

    def to_builder(self) -> NotificationBuilder:
        return NotificationBuilder(
            message=self.message,
            category=self.category,
            ident=self.ident,
            user_id=self.user_id,
            users=self.for_users,
            admins=self.for_admins,
            context=self.context,
            dismissable=self.dismissable,
        )
