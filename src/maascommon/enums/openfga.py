# Copyright 2026 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

OPENFGA_STORE_ID = "00000000000000000000000000"
OPENFGA_AUTHORIZATION_MODEL_ID = "00000000000000000000000000"


class UserType:
    TYPE_NAME = "user"


class GroupType:
    TYPE_NAME = "group"

    MEMBER_RELATION_NAME = "member"


class SystemType:
    TYPE_NAME = "system"

    ADMIN_RELATION_NAME = "admin"
    POOLS_CREATE_RELATION_NAME = "pools.create"
    POOLS_EDIT_RELATION_NAME = "pools.edit"
    POOLS_VIEW_RELATION_NAME = "pools.view"
    POOLS_DELETE_RELATION_NAME = "pools.delete"
    POOLS_MEMBERSHIP_EDIT_RELATION_NAME = "pools.membership.edit"


class PoolType:
    TYPE_NAME = "pool"

    SYSTEM_RELATION_NAME = "member"
    OPERATOR_RELATION_NAME = "operator"
    USER_RELATION_NAME = "user"
    AUDITOR_RELATION_NAME = "auditor"
    POOL_MACHINES_VIEW_RELATION_NAME = "pool.machines.view"
    POOL_MACHINES_ALLOCATE_RELATION_NAME = "pool.machines.allocate"
    POOL_MACHINES_MANAGE_RELATION_NAME = "pool.machines.manage"
