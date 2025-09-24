# Copyright 2024-2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from typing import Callable, Self

from maasservicelayer.context import Context
from maasservicelayer.db.repositories.agentcertificates import (
    AgentCertificatesRepository,
)
from maasservicelayer.db.repositories.agents import AgentsRepository
from maasservicelayer.db.repositories.bootresourcefiles import (
    BootResourceFilesRepository,
)
from maasservicelayer.db.repositories.bootresourcefilesync import (
    BootResourceFileSyncRepository,
)
from maasservicelayer.db.repositories.bootresources import (
    BootResourcesRepository,
)
from maasservicelayer.db.repositories.bootresourcesets import (
    BootResourceSetsRepository,
)
from maasservicelayer.db.repositories.bootsourcecache import (
    BootSourceCacheRepository,
)
from maasservicelayer.db.repositories.bootsources import BootSourcesRepository
from maasservicelayer.db.repositories.bootsourceselections import (
    BootSourceSelectionsRepository,
)
from maasservicelayer.db.repositories.bootstraptokens import (
    BootstrapTokensRepository,
)
from maasservicelayer.db.repositories.consumers import ConsumersRepository
from maasservicelayer.db.repositories.database_configurations import (
    DatabaseConfigurationsRepository,
)
from maasservicelayer.db.repositories.dhcpsnippets import (
    DhcpSnippetsRepository,
)
from maasservicelayer.db.repositories.discoveries import DiscoveriesRepository
from maasservicelayer.db.repositories.dnsdata import DNSDataRepository
from maasservicelayer.db.repositories.dnspublications import (
    DNSPublicationRepository,
)
from maasservicelayer.db.repositories.dnsresources import DNSResourceRepository
from maasservicelayer.db.repositories.domains import DomainsRepository
from maasservicelayer.db.repositories.events import (
    EventsRepository,
    EventTypesRepository,
)
from maasservicelayer.db.repositories.external_auth import (
    ExternalAuthRepository,
)
from maasservicelayer.db.repositories.fabrics import FabricsRepository
from maasservicelayer.db.repositories.filestorage import FileStorageRepository
from maasservicelayer.db.repositories.interfaces import InterfaceRepository
from maasservicelayer.db.repositories.ipranges import IPRangesRepository
from maasservicelayer.db.repositories.machines import MachinesRepository
from maasservicelayer.db.repositories.mdns import MDNSRepository
from maasservicelayer.db.repositories.neighbours import NeighboursRepository
from maasservicelayer.db.repositories.nodegrouptorackcontrollers import (
    NodeGroupToRackControllersRepository,
)
from maasservicelayer.db.repositories.nodes import NodesRepository
from maasservicelayer.db.repositories.notifications import (
    NotificationsRepository,
)
from maasservicelayer.db.repositories.package_repositories import (
    PackageRepositoriesRepository,
)
from maasservicelayer.db.repositories.racks import RacksRepository
from maasservicelayer.db.repositories.rdns import RDNSRepository
from maasservicelayer.db.repositories.reservedips import ReservedIPsRepository
from maasservicelayer.db.repositories.resource_pools import (
    ResourcePoolRepository,
)
from maasservicelayer.db.repositories.scriptresults import (
    ScriptResultsRepository,
)
from maasservicelayer.db.repositories.service_status import (
    ServiceStatusRepository,
)
from maasservicelayer.db.repositories.spaces import SpacesRepository
from maasservicelayer.db.repositories.sshkeys import SshKeysRepository
from maasservicelayer.db.repositories.sslkeys import SSLKeysRepository
from maasservicelayer.db.repositories.staticipaddress import (
    StaticIPAddressRepository,
)
from maasservicelayer.db.repositories.staticroutes import (
    StaticRoutesRepository,
)
from maasservicelayer.db.repositories.subnet_utilization import (
    SubnetUtilizationRepository,
)
from maasservicelayer.db.repositories.subnets import SubnetsRepository
from maasservicelayer.db.repositories.tags import TagsRepository
from maasservicelayer.db.repositories.tokens import TokensRepository
from maasservicelayer.db.repositories.ui_subnets import UISubnetsRepository
from maasservicelayer.db.repositories.users import UsersRepository
from maasservicelayer.db.repositories.vlans import VlansRepository
from maasservicelayer.db.repositories.vmcluster import VmClustersRepository
from maasservicelayer.db.repositories.zones import ZonesRepository
from maasservicelayer.services.agentcertificates import AgentCertificateService
from maasservicelayer.services.agents import AgentsService
from maasservicelayer.services.auth import AuthService
from maasservicelayer.services.base import ServiceCache
from maasservicelayer.services.boot_sources import BootSourcesService
from maasservicelayer.services.bootresourcefiles import (
    BootResourceFilesService,
)
from maasservicelayer.services.bootresourcefilesync import (
    BootResourceFileSyncService,
)
from maasservicelayer.services.bootresources import BootResourceService
from maasservicelayer.services.bootresourcesets import BootResourceSetsService
from maasservicelayer.services.bootsourcecache import BootSourceCacheService
from maasservicelayer.services.bootsourceselections import (
    BootSourceSelectionsService,
)
from maasservicelayer.services.bootstraptoken import BootstrapTokensService
from maasservicelayer.services.configurations import ConfigurationsService
from maasservicelayer.services.consumers import ConsumersService
from maasservicelayer.services.database_configurations import (
    DatabaseConfigurationsService,
)
from maasservicelayer.services.dhcpsnippets import DhcpSnippetsService
from maasservicelayer.services.discoveries import DiscoveriesService
from maasservicelayer.services.dnsdata import DNSDataService
from maasservicelayer.services.dnspublications import DNSPublicationsService
from maasservicelayer.services.dnsresourcerecordsets import (
    V3DNSResourceRecordSetsService,
)
from maasservicelayer.services.dnsresources import DNSResourcesService
from maasservicelayer.services.domains import DomainsService
from maasservicelayer.services.events import EventsService
from maasservicelayer.services.external_auth import ExternalAuthService
from maasservicelayer.services.fabrics import FabricsService
from maasservicelayer.services.filestorage import FileStorageService
from maasservicelayer.services.hooked_configurations import (
    HookedConfigurationsService,
)
from maasservicelayer.services.image_sync import ImageSyncService
from maasservicelayer.services.interfaces import InterfacesService
from maasservicelayer.services.ipranges import IPRangesService
from maasservicelayer.services.leases import LeasesService
from maasservicelayer.services.machines import MachinesService
from maasservicelayer.services.machines_v2 import MachinesV2Service
from maasservicelayer.services.mdns import MDNSService
from maasservicelayer.services.msm import MSMService
from maasservicelayer.services.neighbours import NeighboursService
from maasservicelayer.services.nodegrouptorackcontrollers import (
    NodeGroupToRackControllersService,
)
from maasservicelayer.services.nodes import NodesService
from maasservicelayer.services.notifications import NotificationsService
from maasservicelayer.services.package_repositories import (
    PackageRepositoriesService,
)
from maasservicelayer.services.racks import RacksService
from maasservicelayer.services.rdns import RDNSService
from maasservicelayer.services.reservedips import ReservedIPsService
from maasservicelayer.services.resource_pools import ResourcePoolsService
from maasservicelayer.services.scriptresult import ScriptResultsService
from maasservicelayer.services.secrets import (
    SecretsService,
    SecretsServiceFactory,
)
from maasservicelayer.services.service_status import ServiceStatusService
from maasservicelayer.services.spaces import SpacesService
from maasservicelayer.services.sshkeys import SshKeysService
from maasservicelayer.services.sslkey import SSLKeysService
from maasservicelayer.services.staticipaddress import StaticIPAddressService
from maasservicelayer.services.staticroutes import StaticRoutesService
from maasservicelayer.services.subnet_utilization import (
    V3SubnetUtilizationService,
)
from maasservicelayer.services.subnets import SubnetsService
from maasservicelayer.services.tags import TagsService
from maasservicelayer.services.temporal import TemporalService
from maasservicelayer.services.tokens import TokensService
from maasservicelayer.services.ui_subnets import UISubnetsService
from maasservicelayer.services.users import UsersService
from maasservicelayer.services.vlans import VlansService
from maasservicelayer.services.vmcluster import VmClustersService
from maasservicelayer.services.zones import ZonesService


class CacheForServices:
    def __init__(self):
        self.cache: dict[str, ServiceCache] = {}

    def set(self, name: str, value: ServiceCache) -> None:
        self.cache[name] = value

    def get(self, name: str, fn: Callable) -> ServiceCache:
        """Get the ServiceCache for service named *name*.
        Params:
            - name: class name of the service
            - fn: function to create the cache if it doesn't exists
        Returns:
            ServiceCache: cache for the specified service.
        """
        if name in self.cache:
            return self.cache[name]
        self.set(name, fn())
        return self.cache[name]

    async def close(self) -> None:
        """Perform all the shutdown operations for all caches."""
        for cache in self.cache.values():
            await cache.close()


class ServiceCollectionV3:
    """Provide all v3 services."""

    # Keep them in alphabetical order, please
    agents: AgentsService
    agentcertificates: AgentCertificateService
    auth: AuthService
    boot_resources: BootResourceService
    boot_resource_sets: BootResourceSetsService
    boot_resource_files: BootResourceFilesService
    boot_resource_file_sync: BootResourceFileSyncService
    boot_sources: BootSourcesService
    boot_source_cache: BootSourceCacheService
    boot_source_selections: BootSourceSelectionsService
    bootstraptokens: BootstrapTokensService
    database_configurations: DatabaseConfigurationsService
    configurations: ConfigurationsService
    consumers: ConsumersService
    dhcpsnippets: DhcpSnippetsService
    discoveries: DiscoveriesService
    dnsdata: DNSDataService
    dnspublications: DNSPublicationsService
    dnsresources: DNSResourcesService
    domains: DomainsService
    events: EventsService
    external_auth: ExternalAuthService
    fabrics: FabricsService
    filestorage: FileStorageService
    hooked_configurations: HookedConfigurationsService
    image_sync: ImageSyncService
    interfaces: InterfacesService
    ipranges: IPRangesService
    leases: LeasesService
    machines: MachinesService
    machines_v2: MachinesV2Service
    mdns: MDNSService
    msm: MSMService
    neighbours: NeighboursService
    nodegrouptorackcontrollers: NodeGroupToRackControllersService
    nodes: NodesService
    notifications: NotificationsService
    package_repositories: PackageRepositoriesService
    racks: RacksService
    rdns: RDNSService
    reservedips: ReservedIPsService
    resource_pools: ResourcePoolsService
    scriptresults: ScriptResultsService
    secrets: SecretsService
    service_status: ServiceStatusService
    spaces: SpacesService
    sshkeys: SshKeysService
    sslkeys: SSLKeysService
    staticipaddress: StaticIPAddressService
    staticroutes: StaticRoutesService
    subnets: SubnetsService
    tags: TagsService
    temporal: TemporalService
    tokens: TokensService
    users: UsersService
    v3dnsrrsets: V3DNSResourceRecordSetsService
    v3subnet_utilization: V3SubnetUtilizationService
    vlans: VlansService
    vmclusters: VmClustersService
    ui_subnets: UISubnetsService
    zones: ZonesService

    @classmethod
    async def produce(
        cls,
        context: Context,
        cache: CacheForServices,
    ) -> Self:
        services = cls()
        services.events = EventsService(
            context=context,
            events_repository=EventsRepository(context),
            eventtypes_repository=EventTypesRepository(context),
        )
        services.database_configurations = DatabaseConfigurationsService(
            context=context,
            database_configurations_repository=DatabaseConfigurationsRepository(
                context
            ),
        )
        services.service_status = ServiceStatusService(
            context=context,
            service_status_repository=ServiceStatusRepository(context),
        )
        services.secrets = await SecretsServiceFactory.produce(
            context=context,
            database_configurations_service=services.database_configurations,
            cache=cache.get(
                SecretsService.__name__, SecretsService.build_cache_object
            ),  # type: ignore
        )
        services.configurations = ConfigurationsService(
            context=context,
            database_configurations_service=services.database_configurations,
            secrets_service=services.secrets,
            events_service=services.events,
        )
        services.temporal = TemporalService(
            context=context,
            cache=cache.get(
                TemporalService.__name__, TemporalService.build_cache_object
            ),
        )
        services.msm = MSMService(
            context=context,
            temporal_service=services.temporal,
            config_service=services.configurations,
            secrets_service=services.secrets,
        )
        services.notifications = NotificationsService(
            context=context, repository=NotificationsRepository(context)
        )
        services.tags = TagsService(
            context=context,
            repository=TagsRepository(context),
            events_service=services.events,
            temporal_service=services.temporal,
        )
        services.scriptresults = ScriptResultsService(
            context=context,
            scriptresults_repository=ScriptResultsRepository(context),
        )
        services.dnspublications = DNSPublicationsService(
            context=context,
            temporal_service=services.temporal,
            dnspublication_repository=DNSPublicationRepository(context),
        )
        services.nodes = NodesService(
            context=context,
            secrets_service=services.secrets,
            events_service=services.events,
            scriptresults_service=services.scriptresults,
            dnspublications_service=services.dnspublications,
            nodes_repository=NodesRepository(context),
        )
        services.boot_source_cache = BootSourceCacheService(
            context=context,
            repository=BootSourceCacheRepository(context),
        )
        services.boot_source_selections = BootSourceSelectionsService(
            context=context,
            repository=BootSourceSelectionsRepository(context),
            events_service=services.events,
            boot_source_cache_service=services.boot_source_cache,
        )
        services.boot_sources = BootSourcesService(
            context=context,
            repository=BootSourcesRepository(context),
            boot_source_cache_service=services.boot_source_cache,
            boot_source_selections_service=services.boot_source_selections,
            configuration_service=services.configurations,
            events_service=services.events,
        )
        services.boot_resource_file_sync = BootResourceFileSyncService(
            context=context,
            repository=BootResourceFileSyncRepository(context),
            nodes_service=services.nodes,
        )
        services.boot_resource_files = BootResourceFilesService(
            context=context,
            repository=BootResourceFilesRepository(context),
            boot_resource_file_sync_service=services.boot_resource_file_sync,
            temporal_service=services.temporal,
        )
        services.boot_resource_sets = BootResourceSetsService(
            context=context,
            repository=BootResourceSetsRepository(context),
            boot_resource_files_service=services.boot_resource_files,
            boot_resource_file_sync_service=services.boot_resource_file_sync,
        )
        services.boot_resources = BootResourceService(
            context=context,
            repository=BootResourcesRepository(context),
            boot_resource_sets_service=services.boot_resource_sets,
        )
        services.image_sync = ImageSyncService(
            context=context,
            boot_sources_service=services.boot_sources,
            boot_source_cache_service=services.boot_source_cache,
            boot_source_selections_service=services.boot_source_selections,
            boot_resources_service=services.boot_resources,
            boot_resource_sets_service=services.boot_resource_sets,
            boot_resource_files_service=services.boot_resource_files,
            events_service=services.events,
            configurations_service=services.configurations,
            notifications_service=services.notifications,
            msm_service=services.msm,
        )
        services.vmclusters = VmClustersService(
            context=context, vmcluster_repository=VmClustersRepository(context)
        )
        services.zones = ZonesService(
            context=context,
            nodes_service=services.nodes,
            vmcluster_service=services.vmclusters,
            zones_repository=ZonesRepository(context),
            cache=cache.get(
                ZonesService.__name__, ZonesService.build_cache_object
            ),  # type: ignore
        )
        services.resource_pools = ResourcePoolsService(
            context=context,
            resource_pools_repository=ResourcePoolRepository(context),
        )
        services.machines = MachinesService(
            context=context,
            secrets_service=services.secrets,
            events_service=services.events,
            scriptresults_service=services.scriptresults,
            dnspublications_service=services.dnspublications,
            machines_repository=MachinesRepository(context),
        )
        services.machines_v2 = MachinesV2Service(context=context)
        services.staticipaddress = StaticIPAddressService(
            context=context,
            temporal_service=services.temporal,
            staticipaddress_repository=StaticIPAddressRepository(context),
        )
        services.dhcpsnippets = DhcpSnippetsService(
            context=context,
            dhcpsnippets_repository=DhcpSnippetsRepository(context),
        )
        services.ipranges = IPRangesService(
            context=context,
            temporal_service=services.temporal,
            dhcpsnippets_service=services.dhcpsnippets,
            ipranges_repository=IPRangesRepository(context),
        )
        services.sshkeys = SshKeysService(
            context=context,
            sshkeys_repository=SshKeysRepository(context),
            cache=cache.get(
                SshKeysService.__name__, SshKeysService.build_cache_object
            ),  # type: ignore
        )
        services.sslkeys = SSLKeysService(
            context=context,
            sslkey_repository=SSLKeysRepository(context),
        )
        services.filestorage = FileStorageService(
            context=context, repository=FileStorageRepository(context)
        )
        services.tokens = TokensService(
            context=context, repository=TokensRepository(context)
        )
        services.consumers = ConsumersService(
            context=context,
            repository=ConsumersRepository(context),
            tokens_service=services.tokens,
        )
        services.users = UsersService(
            context=context,
            users_repository=UsersRepository(context),
            staticipaddress_service=services.staticipaddress,
            ipranges_service=services.ipranges,
            nodes_service=services.nodes,
            sshkey_service=services.sshkeys,
            sslkey_service=services.sslkeys,
            notification_service=services.notifications,
            filestorage_service=services.filestorage,
            consumers_service=services.consumers,
            tokens_service=services.tokens,
        )
        services.domains = DomainsService(
            context=context,
            configurations_service=services.configurations,
            dnspublications_service=services.dnspublications,
            users_service=services.users,
            domains_repository=DomainsRepository(context),
        )
        services.dnsresources = DNSResourcesService(
            context=context,
            domains_service=services.domains,
            dnspublications_service=services.dnspublications,
            dnsresource_repository=DNSResourceRepository(context),
        )
        services.interfaces = InterfacesService(
            context=context,
            temporal_service=services.temporal,
            dnspublication_service=services.dnspublications,
            dnsresource_service=services.dnsresources,
            domain_service=services.domains,
            node_service=services.nodes,
            interface_repository=InterfaceRepository(context),
        )
        services.vlans = VlansService(
            context=context,
            temporal_service=services.temporal,
            nodes_service=services.nodes,
            vlans_repository=VlansRepository(context),
        )
        services.spaces = SpacesService(
            context=context,
            vlans_service=services.vlans,
            spaces_repository=SpacesRepository(context),
        )
        services.reservedips = ReservedIPsService(
            context=context,
            temporal_service=services.temporal,
            reservedips_repository=ReservedIPsRepository(context),
        )
        services.staticroutes = StaticRoutesService(
            context=context,
            staticroutes_repository=StaticRoutesRepository(context),
        )
        services.nodegrouptorackcontrollers = NodeGroupToRackControllersService(
            context=context,
            nodegrouptorackcontrollers_repository=NodeGroupToRackControllersRepository(
                context
            ),
        )
        services.subnets = SubnetsService(
            context=context,
            temporal_service=services.temporal,
            staticipaddress_service=services.staticipaddress,
            ipranges_service=services.ipranges,
            staticroutes_service=services.staticroutes,
            reservedips_service=services.reservedips,
            dhcpsnippets_service=services.dhcpsnippets,
            dnspublications_service=services.dnspublications,
            nodegrouptorackcontrollers_service=services.nodegrouptorackcontrollers,
            subnets_repository=SubnetsRepository(context),
        )
        services.dnsdata = DNSDataService(
            context=context,
            dnspublications_service=services.dnspublications,
            domains_service=services.domains,
            dnsresources_service=services.dnsresources,
            dnsdata_repository=DNSDataRepository(context),
        )
        services.fabrics = FabricsService(
            context=context,
            vlans_service=services.vlans,
            subnets_service=services.subnets,
            interfaces_service=services.interfaces,
            fabrics_repository=FabricsRepository(context),
        )
        services.leases = LeasesService(
            context=context,
            dnsresource_service=services.dnsresources,
            node_service=services.nodes,
            staticipaddress_service=services.staticipaddress,
            subnet_service=services.subnets,
            interface_service=services.interfaces,
            iprange_service=services.ipranges,
        )
        services.auth = AuthService(
            context=context,
            secrets_service=services.secrets,
            users_service=services.users,
        )
        services.external_auth = ExternalAuthService(
            context=context,
            secrets_service=services.secrets,
            users_service=services.users,
            external_auth_repository=ExternalAuthRepository(context),
            cache=cache.get(
                ExternalAuthService.__name__,
                ExternalAuthService.build_cache_object,
            ),  # type: ignore
        )
        services.agentcertificates = AgentCertificateService(
            context=context,
            repository=AgentCertificatesRepository(context),
        )
        services.agents = AgentsService(
            context=context,
            repository=AgentsRepository(context),
            configurations_service=services.configurations,
            users_service=services.users,
            agentcertificates_service=services.agentcertificates,
            cache=cache.get(
                AgentsService.__name__, AgentsService.build_cache_object
            ),  # type: ignore
        )
        services.v3dnsrrsets = V3DNSResourceRecordSetsService(
            context=context,
            domains_service=services.domains,
            dnsresource_service=services.dnsresources,
            dnsdata_service=services.dnsdata,
            staticipaddress_service=services.staticipaddress,
            subnets_service=services.subnets,
        )
        services.v3subnet_utilization = V3SubnetUtilizationService(
            context=context,
            subnets_service=services.subnets,
            subnet_utilization_repository=SubnetUtilizationRepository(context),
        )
        services.ui_subnets = UISubnetsService(
            context=context,
            ui_subnets_repository=UISubnetsRepository(context),
            subnets_utilization_service=services.v3subnet_utilization,
        )
        services.mdns = MDNSService(
            context=context, mdns_repository=MDNSRepository(context)
        )
        services.bootstraptokens = BootstrapTokensService(
            context=context,
            repository=BootstrapTokensRepository(context),
        )
        services.racks = RacksService(
            context=context,
            repository=RacksRepository(context),
            agents_service=services.agents,
            bootstraptokens_service=services.bootstraptokens,
            configurations_service=services.configurations,
            secrets_service=services.secrets,
        )
        services.rdns = RDNSService(
            context=context, rdns_repository=RDNSRepository(context)
        )
        services.neighbours = NeighboursService(
            context=context,
            neighbours_repository=NeighboursRepository(context),
        )
        services.discoveries = DiscoveriesService(
            context=context,
            discoveries_repository=DiscoveriesRepository(context),
            mdns_service=services.mdns,
            rdns_service=services.rdns,
            neighbours_service=services.neighbours,
        )
        services.package_repositories = PackageRepositoriesService(
            context=context,
            repository=PackageRepositoriesRepository(context),
            events_service=services.events,
        )
        services.hooked_configurations = HookedConfigurationsService(
            context=context,
            configurations_service=services.configurations,
            temporal_service=services.temporal,
            users_service=services.users,
            vlans_service=services.vlans,
            v3dnsrrsets_service=services.v3dnsrrsets,
        )
        return services
