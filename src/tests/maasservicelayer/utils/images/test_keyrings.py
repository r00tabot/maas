# Copyright 2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).
"""Tests for the images keyring management functions."""

import hashlib
import os
from unittest.mock import mock_open, patch

from maasservicelayer.utils.images import keyrings
from maastesting.factory import factory


class TestWriteKeyring:
    """Tests for `write_keyring().`"""

    def test_writes_keyring_to_file(self) -> None:
        keyring_data = "A keyring! My kingdom for a keyring!"
        keyring_path = os.path.join("/tmp/keyrings", "a-keyring-file")

        expected_data = keyring_data.encode("utf-8")

        with patch(
            "builtins.open", mock_open(read_data=expected_data)
        ) as mock_keyring_file:
            keyrings.write_keyring(keyring_path, keyring_data.encode("utf-8"))

            mock_keyring_file.assert_called_once_with(keyring_path, "wb")
            mock_keyring_file.return_value.__enter__().write.assert_called_once_with(
                expected_data
            )


class TestCalculateKeyringName:
    """Tests for `calculate_keyring_name()`."""

    def test_creates_name_from_url(self) -> None:
        path = "/".join(factory.make_name(size=16) for _ in range(1, 5))
        source_url = f"http://example.com/{path}"

        expected_keyring_name = hashlib.md5(
            source_url.encode("utf8")
        ).hexdigest()
        actual_keyring_name = keyrings.calculate_keyring_name(source_url)

        assert expected_keyring_name == actual_keyring_name
