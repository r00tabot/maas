#  Copyright 2025 Canonical Ltd.  This software is licensed under the
#  GNU Affero General Public License version 3 (see the file LICENSE).
from io import BytesIO
from unittest.mock import MagicMock, Mock, patch

from fastapi import UploadFile
import pytest

from maasapiserver.v3.api.public.models.requests.boot_resources import (
    BootResourceCreateRequest,
    BootResourceFileTypeChoice,
)
from maascommon.enums.boot_resources import BootResourceType
from maasservicelayer.builders.bootresources import BootResourceBuilder
from maasservicelayer.exceptions.catalog import ValidationException
from maasservicelayer.models.bootresources import BootResource
from maasservicelayer.models.bootsourcecache import BootSourceCache
from maasservicelayer.services import ServiceCollectionV3
from maasservicelayer.services.bootresources import BootResourceService
from maasservicelayer.services.bootsourcecache import BootSourceCacheService
from maasservicelayer.services.configurations import ConfigurationsService
from maastesting.factory import factory


class TestBootResourceCreateRequest:
    def create_dummy_binary_upload_file(
        self,
        name: str | None = "test_upload_file.bin",
        size_in_bytes: int = 1024,
    ) -> BytesIO:
        assert size_in_bytes >= 0, "Size of dummy file must be positive"
        file_bytes = BytesIO()
        file_bytes.name = name
        file_bytes.write(b"0" * size_in_bytes)
        file_bytes.seek(0)
        return file_bytes

    @patch(
        "maasapiserver.v3.api.public.models.requests.boot_resources.BootResourceCreateRequest._validate_architecture"
    )
    @patch(
        "maasapiserver.v3.api.public.models.requests.boot_resources.BootResourceCreateRequest._validate_base_image"
    )
    @patch(
        "maasapiserver.v3.api.public.models.requests.boot_resources.BootResourceCreateRequest._validate_name"
    )
    async def test_to_builder(
        self,
        validate_name_mock: MagicMock,
        validate_base_image_mock: MagicMock,
        validate_architecture_mock: MagicMock,
    ) -> None:
        services_mock = Mock(ServiceCollectionV3)

        file = UploadFile(self.create_dummy_binary_upload_file())

        request = BootResourceCreateRequest(
            name="test-name",
            sha256="test-sha256",
            size=123456,
            architecture="amd64/generic",
            file_type=BootResourceFileTypeChoice.TGZ,
            content=file,
            base_image="custom/base",
        )

        validate_name_mock.return_value = request.name
        validate_base_image_mock.return_value = request.base_image
        validate_architecture_mock.return_value = request.architecture

        resource_builder: BootResourceBuilder = await request.to_builder(
            services=services_mock
        )

        assert resource_builder.name == request.name
        assert resource_builder.base_image == request.base_image
        assert resource_builder.architecture == request.architecture
        assert resource_builder.rtype == BootResourceType.UPLOADED

    async def test_validate_name_custom(self) -> None:
        services_mock = Mock(ServiceCollectionV3)

        services_mock.boot_source_cache = Mock(BootSourceCacheService)
        services_mock.boot_source_cache.get_many.return_value = []

        name = "custom/my_custom_image"

        file = UploadFile(self.create_dummy_binary_upload_file())

        request = BootResourceCreateRequest(
            name=name,
            sha256="test-sha256",
            size=123456,
            architecture="amd64/generic",
            file_type=BootResourceFileTypeChoice.TGZ,
            content=file,
        )

        validated_name = await request._validate_name(name, services_mock)

        assert validated_name == "my_custom_image"

    async def test_validate_name_supported(self) -> None:
        services_mock = Mock(ServiceCollectionV3)

        services_mock.boot_source_cache = Mock(BootSourceCacheService)
        services_mock.boot_source_cache.get_many.return_value = []

        name = "ubuntu/noble"

        file = UploadFile(self.create_dummy_binary_upload_file())

        request = BootResourceCreateRequest(
            name=name,
            sha256="test-sha256",
            size=123456,
            architecture="amd64/generic",
            file_type=BootResourceFileTypeChoice.TGZ,
            content=file,
        )
        validated_name = await request._validate_name(name, services_mock)

        assert validated_name == "ubuntu/noble"

    async def test_validate_name_not_supported(self) -> None:
        services_mock = Mock(ServiceCollectionV3)

        services_mock.boot_source_cache = Mock(BootSourceCacheService)
        services_mock.boot_source_cache.get_many.return_value = []

        name = "unsupported/os"

        file = UploadFile(self.create_dummy_binary_upload_file())

        request = BootResourceCreateRequest(
            name=name,
            sha256="test-sha256",
            size=123456,
            architecture="amd64/generic",
            file_type=BootResourceFileTypeChoice.TGZ,
            content=file,
        )
        with pytest.raises(ValidationException) as validation_exception:
            await request._validate_name(name, services_mock)

        assert validation_exception.value.details[0].field == "name"

    async def test_validate_name_centos(self) -> None:
        services_mock = Mock(ServiceCollectionV3)

        services_mock.boot_source_cache = Mock(BootSourceCacheService)
        services_mock.boot_source_cache.get_many.return_value = []

        name = "centos7"

        file = UploadFile(self.create_dummy_binary_upload_file())

        request = BootResourceCreateRequest(
            name=name,
            sha256="test-sha256",
            size=123456,
            architecture="amd64/generic",
            file_type=BootResourceFileTypeChoice.TGZ,
            content=file,
        )
        with pytest.raises(ValidationException) as validation_exception:
            await request._validate_name(name, services_mock)

        assert validation_exception.value.details[0].field == "name"

    async def test_validate_name_reserved_name(self) -> None:
        services_mock = Mock(ServiceCollectionV3)

        services_mock.boot_source_cache = Mock(BootSourceCacheService)
        services_mock.boot_source_cache.get_many.return_value = [
            BootSourceCache(
                id=0,
                os="ubuntu",
                arch="amd64",
                subarch="generic",
                release="noble",
                label="",
                boot_source_id=0,
                extra={},
            )
        ]

        name = "ubuntu/noble"

        file = UploadFile(self.create_dummy_binary_upload_file())

        request = BootResourceCreateRequest(
            name=name,
            sha256="test-sha256",
            size=123456,
            architecture="amd64/generic",
            file_type=BootResourceFileTypeChoice.TGZ,
            content=file,
        )
        with pytest.raises(ValidationException) as validation_exception:
            await request._validate_name(name, services_mock)

        assert validation_exception.value.details[0].field == "name"

    async def test_validate_name_reserved_osystem(self) -> None:
        services_mock = Mock(ServiceCollectionV3)

        services_mock.boot_source_cache = Mock(BootSourceCacheService)
        services_mock.boot_source_cache.get_many.return_value = [
            BootSourceCache(
                id=0,
                os="ubuntu",
                arch="amd64",
                subarch="generic",
                release="noble",
                label="",
                boot_source_id=0,
                extra={},
            )
        ]

        name = "ubuntu"

        file = UploadFile(self.create_dummy_binary_upload_file())

        request = BootResourceCreateRequest(
            name=name,
            sha256="test-sha256",
            size=123456,
            architecture="amd64/generic",
            file_type=BootResourceFileTypeChoice.TGZ,
            content=file,
        )
        with pytest.raises(ValidationException) as validation_exception:
            await request._validate_name(name, services_mock)

        assert validation_exception.value.details[0].field == "name"

    async def test_validate_name_reserved_release(self) -> None:
        services_mock = Mock(ServiceCollectionV3)

        services_mock.boot_source_cache = Mock(BootSourceCacheService)
        services_mock.boot_source_cache.get_many.return_value = [
            BootSourceCache(
                id=0,
                os="ubuntu",
                arch="amd64",
                subarch="generic",
                release="noble",
                label="",
                boot_source_id=0,
                extra={},
            )
        ]

        name = "noble"

        file = UploadFile(self.create_dummy_binary_upload_file())

        request = BootResourceCreateRequest(
            name=name,
            sha256="test-sha256",
            size=123456,
            architecture="amd64/generic",
            file_type=BootResourceFileTypeChoice.TGZ,
            content=file,
        )
        with pytest.raises(ValidationException) as validation_exception:
            await request._validate_name(name, services_mock)

        assert validation_exception.value.details[0].field == "name"

    async def test_validate_base_image(self) -> None:
        services_mock = Mock(ServiceCollectionV3)

        base_image = "ubuntu/noble"
        name = "custom/my_custom_image"
        architecture = "amd64/generic"
        rtype = BootResourceType.UPLOADED

        existing_resource = BootResource(
            id=1,
            name=name,
            architecture=architecture,
            rtype=rtype,
            rolling=False,
            extra={},
            base_image=base_image,
        )

        services_mock.boot_resources = Mock(BootResourceService)
        services_mock.boot_resources.get_one.return_value = existing_resource

        services_mock.configurations = Mock(ConfigurationsService)
        services_mock.configurations.get_many.return_value = []

        file = UploadFile(self.create_dummy_binary_upload_file())

        request = BootResourceCreateRequest(
            name=name,
            sha256="test-sha256",
            size=123456,
            architecture=architecture,
            file_type=BootResourceFileTypeChoice.TGZ,
            content=file,
        )

        validated_base_image = await request._validate_base_image(
            None, name, architecture, rtype, services_mock
        )

        assert validated_base_image == base_image

    async def test_validate_base_image_windows_does_not_require_base_image(
        self,
    ) -> None:
        services_mock = Mock(ServiceCollectionV3)

        services_mock.boot_resources = Mock(BootResourceService)
        services_mock.boot_resources.get_one.return_value = []

        services_mock.configurations = Mock(ConfigurationsService)
        services_mock.configurations.get_many.return_value = []

        base_image = None
        name = f"windows/{factory.make_name()}"
        architecture = "amd64/generic"
        rtype = BootResourceType.UPLOADED

        file = UploadFile(self.create_dummy_binary_upload_file())

        request = BootResourceCreateRequest(
            name=name,
            sha256="test-sha256",
            size=123456,
            architecture=architecture,
            file_type=BootResourceFileTypeChoice.TGZ,
            content=file,
        )

        validated_base_image = await request._validate_base_image(
            base_image, name, architecture, rtype, services_mock
        )

        assert validated_base_image == ""

    async def test_validate_base_image_esxi_does_not_require_base_image(
        self,
    ) -> None:
        services_mock = Mock(ServiceCollectionV3)

        services_mock.boot_resources = Mock(BootResourceService)
        services_mock.boot_resources.get_one.return_value = []

        services_mock.configurations = Mock(ConfigurationsService)
        services_mock.configurations.get_many.return_value = []

        base_image = None
        name = f"esxi/{factory.make_name()}"
        architecture = "amd64/generic"
        rtype = BootResourceType.UPLOADED

        file = UploadFile(self.create_dummy_binary_upload_file())

        request = BootResourceCreateRequest(
            name=name,
            sha256="test-sha256",
            size=123456,
            architecture=architecture,
            file_type=BootResourceFileTypeChoice.TGZ,
            content=file,
        )

        validated_base_image = await request._validate_base_image(
            base_image, name, architecture, rtype, services_mock
        )

        assert validated_base_image == ""

    async def test_validate_base_image_rhel_does_not_require_base_image(
        self,
    ) -> None:
        services_mock = Mock(ServiceCollectionV3)

        services_mock.boot_resources = Mock(BootResourceService)
        services_mock.boot_resources.get_one.return_value = []

        services_mock.configurations = Mock(ConfigurationsService)
        services_mock.configurations.get_many.return_value = []

        base_image = None
        name = f"rhel/{factory.make_name()}"
        architecture = "amd64/generic"
        rtype = BootResourceType.UPLOADED

        file = UploadFile(self.create_dummy_binary_upload_file())

        request = BootResourceCreateRequest(
            name=name,
            sha256="test-sha256",
            size=123456,
            architecture=architecture,
            file_type=BootResourceFileTypeChoice.TGZ,
            content=file,
        )

        validated_base_image = await request._validate_base_image(
            base_image, name, architecture, rtype, services_mock
        )

        assert validated_base_image == ""

    async def test_validate_architecture_usable(self) -> None:
        services_mock = Mock(ServiceCollectionV3)

        services_mock.boot_resources = Mock(BootResourceService)
        services_mock.boot_resources.get_usable_architectures.return_value = [
            "amd64/generic",
        ]

        name = f"custom/{factory.make_name()}"
        architecture = "amd64/generic"

        file = UploadFile(self.create_dummy_binary_upload_file())

        request = BootResourceCreateRequest(
            name=name,
            sha256="test-sha256",
            size=123456,
            architecture=architecture,
            file_type=BootResourceFileTypeChoice.TGZ,
            content=file,
        )

        validated_base_architecture = await request._validate_architecture(
            architecture, services_mock
        )

        assert validated_base_architecture == architecture

    async def test_validate_architecture_not_usable(self) -> None:
        services_mock = Mock(ServiceCollectionV3)

        services_mock.boot_resources = Mock(BootResourceService)
        services_mock.boot_resources.get_usable_architectures.return_value = [
            "amd64/generic",
        ]

        name = f"custom/{factory.make_name()}"
        architecture = "arm64/generic"

        file = UploadFile(self.create_dummy_binary_upload_file())

        request = BootResourceCreateRequest(
            name=name,
            sha256="test-sha256",
            size=123456,
            architecture=architecture,
            file_type=BootResourceFileTypeChoice.TGZ,
            content=file,
        )

        with pytest.raises(ValidationException) as validation_exception:
            _ = await request._validate_architecture(
                architecture, services_mock
            )

        assert validation_exception.value.details[0].field == "architecture"

    async def test_validate_architecture_invalid_format(self) -> None:
        services_mock = Mock(ServiceCollectionV3)

        name = f"custom/{factory.make_name()}"
        architecture = "asdfghjkl;./"

        file = UploadFile(self.create_dummy_binary_upload_file())

        request = BootResourceCreateRequest(
            name=name,
            sha256="test-sha256",
            size=123456,
            architecture=architecture,
            file_type=BootResourceFileTypeChoice.TGZ,
            content=file,
        )

        with pytest.raises(ValidationException) as validation_exception:
            _ = await request._validate_architecture(
                architecture, services_mock
            )

        assert validation_exception.value.details[0].field == "architecture"
