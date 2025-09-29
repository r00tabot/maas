#  Copyright 2025 Canonical Ltd.  This software is licensed under the
#  GNU Affero General Public License version 3 (see the file LICENSE).
import os
from pathlib import Path

from maascommon.path import get_maas_data_path

StrOrBytesPath = str | bytes | os.PathLike[str] | os.PathLike[bytes]
FileDescriptorOrPath = int | StrOrBytesPath


def get_bootresource_store_path() -> Path:
    return Path(get_maas_data_path("image-storage"))


def file_descriptor_or_path_to_path(
    fd_or_path: FileDescriptorOrPath,
) -> StrOrBytesPath:
    if isinstance(fd_or_path, int):
        if os.name == "posix":
            # On Linux, file descriptors can be accessed via `/proc/self/fd/{fd}`
            return f"/proc/self/fd/{fd_or_path}"
        else:
            raise ValueError(
                "File descriptor handling is not supported on this OS."
            )
    return fd_or_path
