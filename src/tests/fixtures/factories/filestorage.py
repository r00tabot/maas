#  Copyright 2025 Canonical Ltd.  This software is licensed under the
#  GNU Affero General Public License version 3 (see the file LICENSE).
from base64 import b64encode

from maasservicelayer.models.filestorage import FileStorage
from tests.maasapiserver.fixtures.db import Fixture


async def create_test_filestorage_entry(
    fixture: Fixture, **extra_details
) -> FileStorage:
    filestorage = {
        "filename": "test_file",
        # `content`'s type is `bytes` in service layer, base64-encoded `str` in db
        "content": b64encode(b"content").decode("utf-8"),
        "key": "key",
        "owner_id": None,
    }
    filestorage.update(extra_details)
    [created_filestorage] = await fixture.create(
        "maasserver_filestorage", [filestorage]
    )
    return FileStorage(**created_filestorage)
