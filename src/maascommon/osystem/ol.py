# Copyright 2023-2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""OL Operating System."""

import re

from maascommon.osystem import BOOT_IMAGE_PURPOSE, OperatingSystem

# Regex matcher that is used to check if the release is supported. The release
# name just has to start with 'ol' to be supported but the major, minor,
# and title are found if available to help format the title.
DISTRO_MATCHER = re.compile(
    r"^ol(?P<major>\d+)?(\.(?P<minor>\d+))?(-(?P<title>.+))?$", re.I
)
DISTRO_SERIES_DEFAULT = "ol9"


class OL(OperatingSystem):
    """OL operating system."""

    name = "ol"
    title = "Oracle Linux"

    def get_boot_image_purposes(self):
        """Gets the purpose of each boot image."""
        return [BOOT_IMAGE_PURPOSE.XINSTALL]

    def get_default_release(self):
        """Gets the default release to use when a release is not
        explicit."""
        return DISTRO_SERIES_DEFAULT

    def get_release_title(self, release):
        """Return the title for the given release."""
        matched = DISTRO_MATCHER.match(release)
        if matched is None:
            # This should never happen as is_release_supported will return
            # false but just in case it does...
            return f"{self.title} {release}"

        ret = self.title
        major = matched.group("major")
        minor = matched.group("minor")
        title = matched.group("title")

        if major is not None:
            ret += f" {major}"
        if minor is not None:
            ret += f".{minor}"
        if title is not None:
            ret += f" {title}"

        return ret
