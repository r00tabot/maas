# Copyright 2026 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from maascommon.utils.ulid import generate_ulid


class TestUlid:
    def _is_ulid(self, value: str) -> bool:
        if len(value) != 26:
            return False

        crockford_base32 = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
        return all(c in crockford_base32 for c in value.upper())

    def test_ulid_uniqueness_and_correctness(self, monkeypatch):
        ulids = {generate_ulid() for _ in range(100)}
        assert len(ulids) == 100  # Ensure all ULIDs are unique
        for u in ulids:
            assert self._is_ulid(u) is True
        assert 1 == 2
