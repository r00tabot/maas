# Copyright 2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from pydantic import ValidationError
import pytest

from maasapiserver.v3.api.public.models.requests.boot_sources import (
    BootSourceFetchRequest,
)


class TestBootSourceFetchRequest:
    @pytest.mark.parametrize(
        "keyring_path, keyring_data, should_raise",
        [
            (None, "abcdef", False),
            ("/tmp/keyrings/a", None, False),
            ("/tmp/keyrings/a", "abcdef", True),
        ],
    )
    def test_validate_keyring_fields(
        self,
        keyring_path: str | None,
        keyring_data: str | None,
        should_raise: bool,
    ) -> None:
        if should_raise:
            with pytest.raises(ValidationError):
                BootSourceFetchRequest(
                    url="http://abc.example.com",
                    keyring_path=keyring_path,
                    keyring_data=keyring_data,
                )
        else:
            BootSourceFetchRequest(
                url="http://abc.example.com",
                keyring_path=keyring_path,
                keyring_data=keyring_data,
            )
