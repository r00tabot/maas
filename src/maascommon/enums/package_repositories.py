# Copyright 2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from enum import StrEnum


class MainArchesEnum(StrEnum):
    AMD64 = "amd64"
    I386 = "i386"


class PortsArchesEnum(StrEnum):
    ARMHF = "armhf"
    ARM64 = "arm64"
    PPC64EL = "ppc64el"
    S390X = "s390x"


class KnownArchesEnum(StrEnum):
    AMD64 = "amd64"
    I386 = "i386"
    ARMHF = "armhf"
    ARM64 = "arm64"
    PPC64EL = "ppc64el"
    S390X = "s390x"


class KnownComponentsEnum(StrEnum):
    MAIN = "main"
    RESTRICTED = "restricted"
    UNIVERSE = "universe"
    MULTIVERSE = "multiverse"


class ComponentsToDisableEnum(StrEnum):
    RESTRICTED = "restricted"
    UNIVERSE = "universe"
    MULTIVERSE = "multiverse"


class PocketsToDisableEnum(StrEnum):
    UPDATES = "updates"
    SECURITY = "security"
    BACKPORTS = "backports"
