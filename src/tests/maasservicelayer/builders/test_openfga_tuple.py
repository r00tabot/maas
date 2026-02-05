# Copyright 2026 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import pytest

from maasservicelayer.builders.openfga_tuple import OpenFGATupleBuilder


class TestOpenFGATupleBuilder:
    def test_default_initialization(self):
        builder = OpenFGATupleBuilder()
        assert builder.populated_fields() == {}

    def test_build_user_is_group_member_tuple(self):
        user_id = "user-123"
        group_id = "group-456"
        builder = OpenFGATupleBuilder.build_user_is_group_member_tuple(
            user_id, group_id
        )

        assert builder.user == f"user:{user_id}"
        assert builder.user_type == "user"
        assert builder.relation == "member"
        assert builder.object_id == group_id
        assert builder.object_type == "group"

    def test_build_user_is_system_admin_tuple(self):
        user_id = "admin-789"
        builder = OpenFGATupleBuilder.build_user_is_system_admin_tuple(user_id)

        assert builder.user == f"user:{user_id}"
        assert builder.user_type == "user"
        assert builder.relation == "admin"
        assert builder.object_id == "system"
        assert builder.object_type == "system"

    def test_build_group_is_system_admin_tuple(self):
        group_id = "admins"
        builder = OpenFGATupleBuilder.build_group_is_system_admin_tuple(
            group_id
        )

        assert builder.user == f"group:{group_id}#member"
        assert builder.user_type == "userset"
        assert builder.relation == "admin"
        assert builder.object_id == "system"
        assert builder.object_type == "system"

    def test_build_system_controls_pool_tuple(self):
        """Ensure the system-to-pool relationship is correctly built."""
        pool_id = "pool-99"
        builder = OpenFGATupleBuilder.build_system_controls_pool_tuple(pool_id)

        assert builder.user == "system:system"
        assert builder.user_type == "user"
        assert builder.relation == "system"
        assert builder.object_id == pool_id
        assert builder.object_type == "pool"

    @pytest.mark.parametrize(
        "method_name, relation",
        [
            ("build_user_is_pool_user_tuple", "user"),
            ("build_user_is_pool_auditor_tuple", "auditor"),
            ("build_user_is_pool_operator_tuple", "operator"),
        ],
    )
    def test_user_pool_builders(self, method_name, relation):
        """Test all user-to-pool relationship factory methods."""
        user_id = "u1"
        pool_id = "p1"
        method = getattr(OpenFGATupleBuilder, method_name)
        builder = method(user_id, pool_id)

        assert builder.user == f"user:{user_id}"
        assert builder.user_type == "user"
        assert builder.relation == relation
        assert builder.object_id == pool_id
        assert builder.object_type == "pool"

    @pytest.mark.parametrize(
        "method_name, relation",
        [
            ("build_group_is_pool_user_tuple", "user"),
            ("build_group_is_pool_auditor_tuple", "auditor"),
            ("build_group_is_pool_operator_tuple", "operator"),
        ],
    )
    def test_group_pool_builders(self, method_name, relation):
        """Test all group-to-pool relationship factory methods."""
        group_id = "g1"
        pool_id = "p1"
        method = getattr(OpenFGATupleBuilder, method_name)
        builder = method(group_id, pool_id)

        assert builder.user == f"group:{group_id}#member"
        assert builder.user_type == "userset"
        assert builder.relation == relation
        assert builder.object_id == pool_id
        assert builder.object_type == "pool"
