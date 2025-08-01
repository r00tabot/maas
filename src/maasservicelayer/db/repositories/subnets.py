# Copyright 2024-2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from ipaddress import IPv4Address, IPv6Address
from operator import eq
from typing import List, Type

from sqlalchemy import desc, join, or_, select, Table

from maascommon.enums.subnet import RdnsMode
from maasservicelayer.db.filters import Clause, ClauseFactory, QuerySpec
from maasservicelayer.db.repositories.base import BaseRepository
from maasservicelayer.db.tables import IPRangeTable, SubnetTable, VlanTable
from maasservicelayer.exceptions.catalog import (
    BaseExceptionDetail,
    ValidationException,
)
from maasservicelayer.exceptions.constants import PRECONDITION_FAILED
from maasservicelayer.models.fields import IPv4v6Network
from maasservicelayer.models.subnets import Subnet


class SubnetClauseFactory(ClauseFactory):
    @classmethod
    def with_id(cls, id: int) -> Clause:
        return Clause(condition=eq(SubnetTable.c.id, id))

    @classmethod
    def with_vlan_id(cls, vlan_id: int) -> Clause:
        return Clause(condition=eq(SubnetTable.c.vlan_id, vlan_id))

    @classmethod
    def with_fabric_id(cls, fabric_id: int) -> Clause:
        return Clause(
            condition=eq(VlanTable.c.fabric_id, fabric_id),
            joins=[
                join(
                    SubnetTable,
                    VlanTable,
                    eq(SubnetTable.c.vlan_id, VlanTable.c.id),
                )
            ],
        )

    @classmethod
    def with_allow_dns(cls, allow_dns: bool) -> Clause:
        return Clause(condition=eq(SubnetTable.c.allow_dns, allow_dns))

    @classmethod
    def with_rdns_mode(cls, rdns_mode: RdnsMode) -> Clause:
        return Clause(condition=eq(SubnetTable.c.rdns_mode, rdns_mode))

    @classmethod
    def with_not_rdns_mode(cls, rdns_mode: RdnsMode) -> Clause:
        return Clause(condition=(SubnetTable.c.rdns_mode != rdns_mode))

    @classmethod
    def with_cidr_overlap(cls, cidr: IPv4v6Network) -> Clause:
        return Clause(
            condition=or_(
                SubnetTable.c.cidr.op(">>")(cidr),
                SubnetTable.c.cidr.op("<<")(cidr),
            )
        )


class SubnetsRepository(BaseRepository[Subnet]):
    def get_repository_table(self) -> Table:
        return SubnetTable

    def get_model_factory(self) -> Type[Subnet]:
        return Subnet

    async def find_best_subnet_for_ip(
        self, ip: IPv4Address | IPv6Address
    ) -> Subnet | None:
        if isinstance(ip, IPv6Address) and ip.ipv4_mapped is not None:
            ip = ip.ipv4_mapped

        stmt = (
            select(
                SubnetTable,
                VlanTable.c.dhcp_on,
            )
            .select_from(SubnetTable)
            .join(
                VlanTable,
                VlanTable.c.id == SubnetTable.c.vlan_id,
            )
            .order_by(
                desc(VlanTable.c.dhcp_on),
            )
            .where(SubnetTable.c.cidr.op(">>")(ip))
        )

        result = (await self.execute_stmt(stmt)).first()
        if not result:
            return None

        res = result._asdict()
        del res["dhcp_on"]
        return Subnet(**res)

    async def _pre_delete_checks(self, query: QuerySpec) -> None:
        vlan_dhcp_on_and_dynamic_ip_range = (
            select(SubnetTable)
            .join(VlanTable, eq(SubnetTable.c.vlan_id, VlanTable.c.id))
            .join(IPRangeTable, eq(SubnetTable.c.id, IPRangeTable.c.subnet_id))
            .where(eq(VlanTable.c.dhcp_on, True))
            .where(eq(IPRangeTable.c.type, "dynamic"))
            .exists()
        )
        stmt = self.select_all_statement().where(
            vlan_dhcp_on_and_dynamic_ip_range
        )
        # use the query from `delete` to specify which subnet we want to delete
        stmt = query.enrich_stmt(stmt)
        subnet = (await self.execute_stmt(stmt)).one_or_none()
        if subnet:
            raise ValidationException(
                details=[
                    BaseExceptionDetail(
                        type=PRECONDITION_FAILED,
                        message="Cannot delete a subnet that is actively servicing a dynamic "
                        "IP range. (Delete the dynamic range or disable DHCP first.)",
                    )
                ]
            )

    async def delete_one(self, query: QuerySpec) -> Subnet | None:
        await self._pre_delete_checks(query)
        return await super().delete_one(query)

    async def delete_by_id(self, id: int) -> Subnet | None:
        query = QuerySpec(where=Clause(eq(SubnetTable.c.id, id)))
        return await self.delete_one(query)

    async def delete_many(self, query: QuerySpec) -> List[Subnet]:
        raise NotImplementedError("delete_many is not implemented yet.")
