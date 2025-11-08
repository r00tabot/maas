from unittest import mock

import pytest

from maasserver.regiondservices.temporal import RegionTemporalService


@pytest.fixture
def fake_settings():
    class FakeSettings:
        DATABASES = {
            "default": {
                "NAME": "testdb",
                "USER": "testuser",
                "PASSWORD": "testpass",
                "HOST": "localhost",
                "PORT": "5432",
            }
        }

    return FakeSettings()


@mock.patch("maasserver.regiondservices.temporal.atomic_write")
@mock.patch("maasserver.regiondservices.temporal.get_maas_cluster_cert_paths")
@mock.patch("maasserver.regiondservices.temporal.get_maas_data_path")
@mock.patch("maasserver.regiondservices.temporal.RegionConfiguration.open")
@mock.patch("maasserver.regiondservices.temporal.settings")
@mock.patch("maasserver.regiondservices.temporal.django_connection")
def test_configure_environ_filled(
    mock_django_conn,
    mock_settings,
    mock_regionconfig_open,
    mock_get_maas_data_path,
    mock_get_maas_cluster_cert_paths,
    mock_atomic_write,
    fake_settings,
):
    mock_settings.DATABASES = fake_settings.DATABASES
    mock_django_conn._alias = "default"
    mock_regionconfig_open.return_value.__enter__.return_value.broadcast_address = "1.2.3.4"
    mock_regionconfig_open.return_value.__enter__.return_value.maas_url = (
        "http://maas"
    )
    mock_get_maas_data_path.return_value = "/tmp/temporal"
    mock_get_maas_cluster_cert_paths.return_value = ("cert", "key", "cacert")

    captured_environs = []

    class FakeTemplate:
        def substitute(self, environ):
            captured_environs.append(environ)
            return "template-content"

    with mock.patch(
        "maasserver.regiondservices.temporal.load_template",
        side_effect=[FakeTemplate(), FakeTemplate()],
    ):
        service = RegionTemporalService()
        service._configure()

    # Check environ dict from first template
    environ = captured_environs[0]
    assert environ["database"] == "testdb"
    assert environ["user"] == "testuser"
    assert environ["password"] == "testpass"
    assert environ["tls_enabled"] is False
    assert environ["enable_host_verification"] is False
    assert environ["address"] == "localhost:5432"
    assert environ["broadcast_address"] == "1.2.3.4"
    assert environ["config_dir"] == "/tmp/temporal"
    assert environ["cert_file"] == "cert"
    assert environ["key_file"] == "key"
    assert environ["cacert_file"] == "cacert"
    assert environ["connect_attributes"]["application_name"].startswith(
        "maas-temporal-"
    )


@mock.patch("maasserver.regiondservices.temporal.atomic_write")
@mock.patch("maasserver.regiondservices.temporal.get_maas_cluster_cert_paths")
@mock.patch("maasserver.regiondservices.temporal.get_maas_data_path")
@mock.patch("maasserver.regiondservices.temporal.RegionConfiguration.open")
@mock.patch("maasserver.regiondservices.temporal.settings")
@mock.patch("maasserver.regiondservices.temporal.django_connection")
def test_configure_environ_filled_tls_enabled(
    mock_django_conn,
    mock_settings,
    mock_regionconfig_open,
    mock_get_maas_data_path,
    mock_get_maas_cluster_cert_paths,
    mock_atomic_write,
    fake_settings,
):
    mock_settings.DATABASES = fake_settings.DATABASES
    mock_settings.DATABASES["default"]["OPTIONS"] = {"sslmode": "require"}
    mock_django_conn._alias = "default"
    mock_regionconfig_open.return_value.__enter__.return_value.broadcast_address = "1.2.3.4"
    mock_regionconfig_open.return_value.__enter__.return_value.maas_url = (
        "http://maas"
    )
    mock_get_maas_data_path.return_value = "/tmp/temporal"
    mock_get_maas_cluster_cert_paths.return_value = ("cert", "key", "cacert")

    captured_environs = []

    class FakeTemplate:
        def substitute(self, environ):
            captured_environs.append(environ)
            return "template-content"

    with mock.patch(
        "maasserver.regiondservices.temporal.load_template",
        side_effect=[FakeTemplate(), FakeTemplate()],
    ):
        service = RegionTemporalService()
        service._configure()

    # Check environ dict from first template
    environ = captured_environs[0]
    assert environ["tls_enabled"] is True
    assert environ["enable_host_verification"] is False


@mock.patch("maasserver.regiondservices.temporal.atomic_write")
@mock.patch("maasserver.regiondservices.temporal.get_maas_cluster_cert_paths")
@mock.patch("maasserver.regiondservices.temporal.get_maas_data_path")
@mock.patch("maasserver.regiondservices.temporal.RegionConfiguration.open")
@mock.patch("maasserver.regiondservices.temporal.settings")
@mock.patch("maasserver.regiondservices.temporal.django_connection")
def test_configure_environ_filled_require_ca_validation(
    mock_django_conn,
    mock_settings,
    mock_regionconfig_open,
    mock_get_maas_data_path,
    mock_get_maas_cluster_cert_paths,
    mock_atomic_write,
    fake_settings,
):
    mock_settings.DATABASES = fake_settings.DATABASES
    mock_settings.DATABASES["default"]["OPTIONS"] = {"sslmode": "verify-full"}
    mock_django_conn._alias = "default"
    mock_regionconfig_open.return_value.__enter__.return_value.broadcast_address = "1.2.3.4"
    mock_regionconfig_open.return_value.__enter__.return_value.maas_url = (
        "http://maas"
    )
    mock_get_maas_data_path.return_value = "/tmp/temporal"
    mock_get_maas_cluster_cert_paths.return_value = ("cert", "key", "cacert")

    captured_environs = []

    class FakeTemplate:
        def substitute(self, environ):
            captured_environs.append(environ)
            return "template-content"

    with mock.patch(
        "maasserver.regiondservices.temporal.load_template",
        side_effect=[FakeTemplate(), FakeTemplate()],
    ):
        service = RegionTemporalService()
        service._configure()

    # Check environ dict from first template
    environ = captured_environs[0]
    assert environ["tls_enabled"] is True
    assert environ["enable_host_verification"] is True
