#  Copyright 2026 Canonical Ltd.  This software is licensed under the
#  GNU Affero General Public License version 3 (see the file LICENSE).
import functools

from maascommon.openfga.client.sync import SyncOpenFGAClient


def _get_client():
    return SyncOpenFGAClient()


@functools.lru_cache(maxsize=1)
def get_openfga_client():
    return _get_client()
