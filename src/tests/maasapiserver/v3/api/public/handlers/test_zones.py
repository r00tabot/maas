#  Copyright 2024-2025 Canonical Ltd.  This software is licensed under the
#  GNU Affero General Public License version 3 (see the file LICENSE).

from unittest.mock import Mock
from urllib.parse import parse_qs, urlparse

from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from httpx import AsyncClient
import pytest

from maasapiserver.common.api.models.responses.errors import ErrorBodyResponse
from maasapiserver.v3.api.public.models.requests.zones import ZoneRequest
from maasapiserver.v3.api.public.models.responses.zones import (
    ZoneResponse,
    ZonesListResponse,
    ZonesWithSummaryListResponse,
)
from maasapiserver.v3.constants import DEFAULT_ZONE_NAME, V3_API_PREFIX
from maasservicelayer.exceptions.catalog import (
    AlreadyExistsException,
    BadRequestException,
    BaseExceptionDetail,
    PreconditionFailedException,
)
from maasservicelayer.exceptions.constants import (
    CANNOT_DELETE_DEFAULT_ZONE_VIOLATION_TYPE,
    ETAG_PRECONDITION_VIOLATION_TYPE,
    UNIQUE_CONSTRAINT_VIOLATION_TYPE,
)
from maasservicelayer.models.base import ListResult
from maasservicelayer.models.zones import Zone, ZoneWithSummary
from maasservicelayer.services import ServiceCollectionV3
from maasservicelayer.services.zones import ZonesService
from maasservicelayer.utils.date import utcnow
from tests.maasapiserver.v3.api.public.handlers.base import (
    ApiCommonTests,
    Endpoint,
)

DEFAULT_ZONE = Zone(
    id=1,
    name=DEFAULT_ZONE_NAME,
    description="",
    created=utcnow(),
    updated=utcnow(),
)
TEST_ZONE = Zone(
    id=4,
    name="test_zone",
    description="test_description",
    created=utcnow(),
    updated=utcnow(),
)


class TestZonesApi(ApiCommonTests):
    BASE_PATH = f"{V3_API_PREFIX}/zones"
    DEFAULT_ZONE_PATH = f"{BASE_PATH}/1"

    @pytest.fixture
    def user_endpoints(self) -> list[Endpoint]:
        return [
            Endpoint(method="GET", path=f"{V3_API_PREFIX}/zones_with_summary"),
            Endpoint(method="GET", path=f"{self.BASE_PATH}"),
            Endpoint(method="GET", path=f"{self.BASE_PATH}/2"),
        ]

    @pytest.fixture
    def admin_endpoints(self) -> list[Endpoint]:
        return [
            Endpoint(method="PUT", path=f"{self.BASE_PATH}/1"),
            Endpoint(method="POST", path=f"{self.BASE_PATH}"),
            Endpoint(method="DELETE", path=f"{self.BASE_PATH}/2"),
        ]

    async def test_list_other_page(
        self,
        services_mock: ServiceCollectionV3,
        mocked_api_client_user: AsyncClient,
    ) -> None:
        services_mock.zones = Mock(ZonesService)
        services_mock.zones.list.return_value = ListResult[Zone](
            items=[TEST_ZONE], total=2
        )
        response = await mocked_api_client_user.get(f"{self.BASE_PATH}?size=1")
        assert response.status_code == 200
        zones_response = ZonesListResponse(**response.json())
        assert len(zones_response.items) == 1
        assert zones_response.total == 2
        assert zones_response.next == f"{self.BASE_PATH}?page=2&size=1"

    async def test_list_no_other_page(
        self,
        services_mock: ServiceCollectionV3,
        mocked_api_client_user: AsyncClient,
    ) -> None:
        services_mock.zones = Mock(ZonesService)
        services_mock.zones.list.return_value = ListResult[Zone](
            items=[DEFAULT_ZONE, TEST_ZONE], total=2
        )
        response = await mocked_api_client_user.get(f"{self.BASE_PATH}?size=2")
        assert response.status_code == 200
        zones_response = ZonesListResponse(**response.json())
        assert len(zones_response.items) == 2
        assert zones_response.total == 2
        assert zones_response.next is None

    async def test_list_with_summary_no_other_page(
        self,
        services_mock: ServiceCollectionV3,
        mocked_api_client_user: AsyncClient,
    ) -> None:
        zone_with_summary = ZoneWithSummary(
            id=0,
            name="default",
            description="description",
            machines_count=10,
            devices_count=20,
            controllers_count=30,
        )
        services_mock.zones = Mock(ZonesService)
        services_mock.zones.list_with_summary.return_value = ListResult[
            ZoneWithSummary
        ](items=[zone_with_summary], total=1)
        response = await mocked_api_client_user.get(
            f"{V3_API_PREFIX}/zones_with_summary?size=1"
        )
        assert response.status_code == 200
        zones_with_summary_response = ZonesWithSummaryListResponse(
            **response.json()
        )
        assert len(zones_with_summary_response.items) == 1
        assert zones_with_summary_response.total == 1
        assert zones_with_summary_response.next is None
        zone_with_summary_response = zones_with_summary_response.items[0]
        assert zone_with_summary_response.id == 0
        assert zone_with_summary_response.name == "default"
        assert zone_with_summary_response.description == "description"
        assert zone_with_summary_response.machines_count == 10
        assert zone_with_summary_response.devices_count == 20
        assert zone_with_summary_response.controllers_count == 30
        services_mock.zones.list_with_summary.assert_called_with(
            page=1, size=1
        )

    async def test_list_with_summary_other_page(
        self,
        services_mock: ServiceCollectionV3,
        mocked_api_client_user: AsyncClient,
    ) -> None:
        zone_with_summary = ZoneWithSummary(
            id=0,
            name="default",
            description="description",
            machines_count=10,
            devices_count=20,
            controllers_count=30,
        )
        services_mock.zones = Mock(ZonesService)
        services_mock.zones.list_with_summary.return_value = ListResult[
            ZoneWithSummary
        ](items=[zone_with_summary], total=2)
        response = await mocked_api_client_user.get(
            f"{V3_API_PREFIX}/zones_with_summary?size=1"
        )
        assert response.status_code == 200
        zones_with_summary_response = ZonesWithSummaryListResponse(
            **response.json()
        )
        assert len(zones_with_summary_response.items) == 1
        assert zones_with_summary_response.total == 2
        assert (
            zones_with_summary_response.next
            == f"{V3_API_PREFIX}/zones_with_summary?page=2&size=1"
        )

    # GET /zones with filters
    async def test_list_with_filters(
        self,
        services_mock: ServiceCollectionV3,
        mocked_api_client_user: AsyncClient,
    ) -> None:
        services_mock.zones = Mock(ZonesService)
        services_mock.zones.list.return_value = ListResult[Zone](
            items=[TEST_ZONE], total=2
        )

        # Get also the default zone
        response = await mocked_api_client_user.get(
            f"{self.BASE_PATH}?id=1&id=4&size=1"
        )
        assert response.status_code == 200
        zones_response = ZonesListResponse(**response.json())
        assert len(zones_response.items) == 1

        assert zones_response.next is not None
        next_link_params = parse_qs(urlparse(zones_response.next).query)
        assert set(next_link_params["id"]) == {
            str(DEFAULT_ZONE.id),
            str(TEST_ZONE.id),
        }
        assert next_link_params["size"][0] == "1"
        assert next_link_params["page"][0] == "2"

    # GET /zones/{zone_id}
    async def test_get_default(
        self,
        services_mock: ServiceCollectionV3,
        mocked_api_client_user: AsyncClient,
    ) -> None:
        # A "default" zone should be created at startup by the migration scripts.
        services_mock.zones = Mock(ZonesService)
        services_mock.zones.get_by_id.return_value = DEFAULT_ZONE
        response = await mocked_api_client_user.get(self.DEFAULT_ZONE_PATH)
        assert response.status_code == 200
        assert len(response.headers["ETag"]) > 0
        zone_response = ZoneResponse(**response.json())
        assert zone_response.id == 1
        assert zone_response.name == DEFAULT_ZONE_NAME

    async def test_get_404(
        self,
        services_mock: ServiceCollectionV3,
        mocked_api_client_user: AsyncClient,
    ) -> None:
        services_mock.zones = Mock(ZonesService)
        services_mock.zones.get_by_id.return_value = None
        response = await mocked_api_client_user.get(f"{self.BASE_PATH}/100")
        assert response.status_code == 404
        assert "ETag" not in response.headers

        error_response = ErrorBodyResponse(**response.json())
        assert error_response.kind == "Error"
        assert error_response.code == 404

    async def test_get_422(
        self,
        services_mock: ServiceCollectionV3,
        mocked_api_client_user: AsyncClient,
    ) -> None:
        services_mock.zones = Mock(ZonesService)
        services_mock.zones.get_by_id.side_effect = RequestValidationError(
            errors=[]
        )
        response = await mocked_api_client_user.get(f"{self.BASE_PATH}/xyz")
        assert response.status_code == 422
        assert "ETag" not in response.headers

        error_response = ErrorBodyResponse(**response.json())
        assert error_response.kind == "Error"
        assert error_response.code == 422

    # PUT /zones/{zone_id}
    async def test_put(
        self,
        services_mock: ServiceCollectionV3,
        mocked_api_client_admin: AsyncClient,
    ) -> None:
        updated_test_zone = TEST_ZONE
        updated_test_zone.name = "new_name"
        updated_test_zone.description = "new_description"

        update_zone_request = ZoneRequest(
            name="new_name",
            description="new_description",
        )
        services_mock.zones = Mock(ZonesService)
        services_mock.zones.update_by_id.return_value = updated_test_zone

        response = await mocked_api_client_admin.put(
            f"{self.BASE_PATH}/{str(TEST_ZONE.id)}",
            json=jsonable_encoder(update_zone_request),
        )

        assert response.status_code == 200
        assert len(response.headers["ETag"]) > 0

        updated_zone_response = ZoneResponse(**response.json())

        assert updated_zone_response.id == updated_test_zone.id
        assert updated_zone_response.name == updated_test_zone.name
        assert (
            updated_zone_response.description == updated_test_zone.description
        )

    async def test_put_404(
        self,
        services_mock: ServiceCollectionV3,
        mocked_api_client_admin: AsyncClient,
    ) -> None:
        services_mock.zones = Mock(ZonesService)
        services_mock.zones.update_by_id.return_value = None

        update_zone_request = ZoneRequest(
            name="new_name",
            description="new_description",
        )

        response = await mocked_api_client_admin.put(
            f"{self.BASE_PATH}/99",
            json=jsonable_encoder(update_zone_request),
        )

        assert response.status_code == 404
        assert "ETag" not in response.headers

        error_response = ErrorBodyResponse(**response.json())

        assert error_response.kind == "Error"
        assert error_response.code == 404

    async def test_put_422(
        self,
        services_mock: ServiceCollectionV3,
        mocked_api_client_admin: AsyncClient,
    ) -> None:
        services_mock.zones = Mock(ZonesService)
        services_mock.zones.update_by_id.return_value = None

        update_zone_request = ZoneRequest(
            name="new_name",
            description="new_description",
        )

        response = await mocked_api_client_admin.put(
            f"{self.BASE_PATH}/xyz",
            json=jsonable_encoder(update_zone_request),
        )

        assert response.status_code == 422
        assert "ETag" not in response.headers

        error_response = ErrorBodyResponse(**response.json())

        assert error_response.kind == "Error"
        assert error_response.code == 422

    # POST /zones
    async def test_post_201(
        self,
        services_mock: ServiceCollectionV3,
        mocked_api_client_admin: AsyncClient,
    ) -> None:
        zone_request = ZoneRequest(
            name=TEST_ZONE.name, description=TEST_ZONE.description
        )
        services_mock.zones = Mock(ZonesService)
        services_mock.zones.create.return_value = TEST_ZONE
        response = await mocked_api_client_admin.post(
            self.BASE_PATH, json=jsonable_encoder(zone_request)
        )
        assert response.status_code == 201
        assert len(response.headers["ETag"]) > 0
        zone_response = ZoneResponse(**response.json())
        assert zone_response.id > 1
        assert zone_response.name == zone_request.name
        assert zone_response.description == zone_request.description
        assert (
            zone_response.hal_links.self.href
            == f"{self.BASE_PATH}/{zone_response.id}"
        )

    async def test_post_default_parameters(
        self,
        services_mock: ServiceCollectionV3,
        mocked_api_client_admin: AsyncClient,
    ) -> None:
        zone_request = ZoneRequest(name="myzone", description=None)
        services_mock.zones = Mock(ZonesService)
        services_mock.zones.create.return_value = Zone(
            id=2,
            name="myzone",
            description="",
            created=utcnow(),
            updated=utcnow(),
        )
        response = await mocked_api_client_admin.post(
            self.BASE_PATH, json=jsonable_encoder(zone_request)
        )
        assert response.status_code == 201
        zone_response = ZoneResponse(**response.json())
        assert zone_response.description == ""

    async def test_post_409(
        self,
        services_mock: ServiceCollectionV3,
        mocked_api_client_admin: AsyncClient,
    ) -> None:
        zone_request = ZoneRequest(name="myzone", description=None)
        services_mock.zones = Mock(ZonesService)
        services_mock.zones.create.side_effect = [
            TEST_ZONE,
            AlreadyExistsException(
                details=[
                    BaseExceptionDetail(
                        type=UNIQUE_CONSTRAINT_VIOLATION_TYPE,
                        message="A resource with such identifiers already exist.",
                    )
                ]
            ),
        ]
        response = await mocked_api_client_admin.post(
            self.BASE_PATH, json=jsonable_encoder(zone_request)
        )
        assert response.status_code == 201

        response = await mocked_api_client_admin.post(
            self.BASE_PATH, json=jsonable_encoder(zone_request)
        )
        assert response.status_code == 409

        error_response = ErrorBodyResponse(**response.json())
        assert error_response.kind == "Error"
        assert error_response.code == 409
        assert len(error_response.details) == 1
        assert error_response.details[0].type == "UniqueConstraintViolation"
        assert "already exist" in error_response.details[0].message

    @pytest.mark.parametrize(
        "zone_request",
        [
            {"name": ""},
            {"name": "-myzone"},
            {"name": "Hello$Zone"},
        ],
    )
    async def test_post_422(
        self,
        services_mock: ServiceCollectionV3,
        mocked_api_client_admin: AsyncClient,
        zone_request: dict[str, str],
    ) -> None:
        services_mock.zones = Mock(ZonesService)
        services_mock.zones.create.side_effect = ValueError(
            "Invalid entity name."
        )
        response = await mocked_api_client_admin.post(
            self.BASE_PATH, json=zone_request
        )
        assert response.status_code == 422

        error_response = ErrorBodyResponse(**response.json())
        assert error_response.kind == "Error"
        assert error_response.code == 422

    # DELETE /zones/{id}
    async def test_delete_default_zone(
        self,
        services_mock: ServiceCollectionV3,
        mocked_api_client_admin: AsyncClient,
    ) -> None:
        services_mock.zones = Mock(ZonesService)
        services_mock.zones.delete_by_id.side_effect = BadRequestException(
            details=[
                BaseExceptionDetail(
                    type=CANNOT_DELETE_DEFAULT_ZONE_VIOLATION_TYPE,
                    message="The default zone can not be deleted.",
                )
            ]
        )

        response = await mocked_api_client_admin.delete(self.DEFAULT_ZONE_PATH)

        error_response = ErrorBodyResponse(**response.json())
        assert response.status_code == 400
        assert error_response.code == 400
        assert error_response.message == "Bad request."
        assert (
            error_response.details[0].type
            == CANNOT_DELETE_DEFAULT_ZONE_VIOLATION_TYPE
        )

    async def test_delete_resource(
        self,
        services_mock: ServiceCollectionV3,
        mocked_api_client_admin: AsyncClient,
    ) -> None:
        services_mock.zones = Mock(ZonesService)
        services_mock.zones.delete_by_id.side_effect = None
        response = await mocked_api_client_admin.delete(
            f"{self.BASE_PATH}/100"
        )
        assert response.status_code == 204

    async def test_delete_with_etag(
        self,
        services_mock: ServiceCollectionV3,
        mocked_api_client_admin: AsyncClient,
    ) -> None:
        services_mock.zones = Mock(ZonesService)
        services_mock.zones.delete_by_id.side_effect = [
            PreconditionFailedException(
                details=[
                    BaseExceptionDetail(
                        type=ETAG_PRECONDITION_VIOLATION_TYPE,
                        message="The resource etag 'wrong_etag' did not match 'my_etag'.",
                    )
                ]
            ),
            None,
        ]

        failed_response = await mocked_api_client_admin.delete(
            f"{self.BASE_PATH}/100",
            headers={"if-match": "wrong_etag"},
        )
        assert failed_response.status_code == 412
        error_response = ErrorBodyResponse(**failed_response.json())
        assert error_response.code == 412
        assert error_response.message == "A precondition has failed."
        assert (
            error_response.details[0].type == ETAG_PRECONDITION_VIOLATION_TYPE
        )

        response = await mocked_api_client_admin.delete(
            f"{self.BASE_PATH}/100",
            headers={"if-match": "my_etag"},
        )
        assert response.status_code == 204
