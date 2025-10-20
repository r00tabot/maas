# Copyright 2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

import difflib
import inspect

import uvicorn.protocols.http.h11_impl as h11_impl

from maasapiserver.tls import TLSPatchedH11Protocol


class TestTLSPatchedH11Protocol:
    def test_handle_events_is_identical_except_patch(self):
        """
        We monkey patched uvicorn H11Protocol so to include the information about TSL. This test is going to fail if you are
        upgrading to a newer version of uvicorn and that function has changed.

        In order to fix this test, please take the new implementation of handle_events and update our class accordingly.
        """

        original_src = inspect.getsource(h11_impl.H11Protocol.handle_events)
        patched_src = inspect.getsource(TLSPatchedH11Protocol.handle_events)

        # Normalize indentation
        original_lines = [
            line.strip() for line in original_src.splitlines() if line.strip()
        ]
        patched_lines = [
            line.strip() for line in patched_src.splitlines() if line.strip()
        ]

        filtered_patched = []
        in_patch_block = False
        for line in patched_lines:
            # Remove the patch
            if "### BEGIN PATCH" in line:
                in_patch_block = True
                continue
            elif "### END PATCH" in line:
                in_patch_block = False
                continue
            if not in_patch_block:
                filtered_patched.append(line)

        diff = list(
            difflib.unified_diff(original_lines, filtered_patched, lineterm="")
        )

        assert not diff, (
            "handle_events differs from uvicorn's version beyond the TLS patch."
        )
