from unittest import mock

import pytest

from maasserver.management.commands.dbupgrade import Command


@pytest.fixture
def mock_connections():
    with mock.patch(
        "maasserver.management.commands.dbupgrade.connections"
    ) as connections:
        yield connections


@pytest.fixture
def mock_get_path():
    with mock.patch(
        "maasserver.management.commands.dbupgrade.get_path"
    ) as get_path:
        get_path.side_effect = lambda x: x
        yield get_path


@pytest.fixture
def mock_subprocess():
    with mock.patch(
        "maasserver.management.commands.dbupgrade.subprocess.check_output"
    ) as check_output:
        yield check_output


@pytest.fixture
def mock_os_path_join():
    with mock.patch(
        "maasserver.management.commands.dbupgrade.os.path.join"
    ) as path_join:
        path_join.side_effect = lambda *args: "/".join(args)
        yield path_join


@pytest.fixture
def fake_cursor():
    cursor = mock.MagicMock()
    cursor.fetchone.side_effect = [
        [None],  # temporal.schema_version does not exist
        [None],  # temporal_visibility.schema_version does not exist
    ]
    return cursor


@pytest.fixture
def fake_conn(fake_cursor):
    conn = mock.MagicMock()
    conn.get_connection_params.return_value = {
        "host": "localhost",
        "port": "5432",
        "dbname": "testdb",
        "user": "testuser",
        "password": "testpass",
        "sslmode": "prefer",
    }
    conn.cursor.return_value.__enter__.return_value = fake_cursor
    return conn


@pytest.fixture
def fake_conn_ssl(fake_cursor):
    conn = mock.MagicMock()
    conn.get_connection_params.return_value = {
        "host": "localhost",
        "port": "5432",
        "dbname": "testdb",
        "user": "testuser",
        "password": "testpass",
        "sslmode": "require",
    }
    conn.cursor.return_value.__enter__.return_value = fake_cursor
    return conn


def test_temporal_migration_new_schema(
    mock_connections,
    mock_get_path,
    mock_subprocess,
    mock_os_path_join,
    fake_conn,
    fake_cursor,
):
    mock_connections.__getitem__.return_value = fake_conn

    Command._temporal_migration("default")

    # There should be 4 calls to subprocess.check_output
    assert mock_subprocess.call_count == 4

    # Extract all calls
    calls = [call[0][0] for call in mock_subprocess.call_args_list]

    temporal_base = [
        "/usr/bin/temporal-sql-tool",
        "--plugin",
        "postgres12",
        "--endpoint",
        "localhost",
        "--port",
        "5432",
        "--database",
        "testdb",
        "--ca",
        "search_path=temporal",
        "--user",
        "testuser",
        "--password",
        "testpass",
    ]

    temporal_visibility_base = [
        "/usr/bin/temporal-sql-tool",
        "--plugin",
        "postgres12",
        "--endpoint",
        "localhost",
        "--port",
        "5432",
        "--database",
        "testdb",
        "--ca",
        "search_path=temporal_visibility",
        "--user",
        "testuser",
        "--password",
        "testpass",
    ]

    # 1. setup-schema for temporal
    assert calls[0][:15] == temporal_base
    assert calls[0][15:] == ["setup-schema", "-v", "0.0"]

    # 2. setup-schema for temporal_visibility
    assert calls[1][:15] == temporal_visibility_base
    assert calls[1][15:] == ["setup-schema", "-v", "0.0"]

    # 3. update-schema for temporal
    assert calls[2][:15] == temporal_base
    assert calls[2][15:] == [
        "update-schema",
        "-d",
        "/var/lib/temporal/schema/temporal/versioned",
    ]

    # 4. update-schema for temporal_visibility
    assert calls[3][:15] == temporal_visibility_base
    assert calls[3][15:] == [
        "update-schema",
        "-d",
        "/var/lib/temporal/schema/visibility/versioned",
    ]


def test_temporal_migration_with_ssl(
    mock_connections,
    mock_get_path,
    mock_subprocess,
    mock_os_path_join,
    fake_conn_ssl,
    fake_cursor,
):
    mock_connections.__getitem__.return_value = fake_conn_ssl

    Command._temporal_migration("default")

    # There should be 4 calls to subprocess.check_output
    assert mock_subprocess.call_count == 4

    # Extract all calls
    calls = [call[0][0] for call in mock_subprocess.call_args_list]

    temporal_base = [
        "/usr/bin/temporal-sql-tool",
        "--plugin",
        "postgres12",
        "--endpoint",
        "localhost",
        "--port",
        "5432",
        "--database",
        "testdb",
        "--tls",
        "--ca",
        "search_path=temporal",
        "--user",
        "testuser",
        "--password",
        "testpass",
    ]

    temporal_visibility_base = [
        "/usr/bin/temporal-sql-tool",
        "--plugin",
        "postgres12",
        "--endpoint",
        "localhost",
        "--port",
        "5432",
        "--database",
        "testdb",
        "--tls",
        "--ca",
        "search_path=temporal_visibility",
        "--user",
        "testuser",
        "--password",
        "testpass",
    ]

    # 1. setup-schema for temporal
    assert calls[0][:16] == temporal_base
    assert calls[0][16:] == ["setup-schema", "-v", "0.0"]

    # 2. setup-schema for temporal_visibility
    assert calls[1][:16] == temporal_visibility_base
    assert calls[1][16:] == ["setup-schema", "-v", "0.0"]

    # 3. update-schema for temporal
    assert calls[2][:16] == temporal_base
    assert calls[2][16:] == [
        "update-schema",
        "-d",
        "/var/lib/temporal/schema/temporal/versioned",
    ]

    # 4. update-schema for temporal_visibility
    assert calls[3][:16] == temporal_visibility_base
    assert calls[3][16:] == [
        "update-schema",
        "-d",
        "/var/lib/temporal/schema/visibility/versioned",
    ]
