# Copyright 2014-2025 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Tests for converters utilities."""

from textwrap import dedent

from maasserver.utils.converters import (
    machine_readable_bytes,
    round_size_to_nearest_block,
    round_size_to_nearest_power_of_2_in_gib,
    systemd_interval_to_calendar,
    XMLToYAML,
)
from maastesting.testcase import MAASTestCase


class TestXMLToYAML(MAASTestCase):
    def test_xml_to_yaml_converts_xml(self):
        # This test is similar to the test above but this one
        # checks that tags with colons works as expected.
        xml = """
        <list xmlns:lldp="lldp" xmlns:lshw="lshw">
         <lldp:lldp label="LLDP neighbors"/>
         <lshw:list>Some Content</lshw:list>
        </list>
        """
        expected_result = dedent(
            """\
        - list:
          - lldp:lldp:
            label: LLDP neighbors
          - lshw:list:
            Some Content
        """
        )
        yml = XMLToYAML(xml)
        self.assertEqual(yml.convert(), expected_result)


class TestMachineReadableBytes(MAASTestCase):
    """Testing the human->machine byte count converter"""

    def test_suffixes(self):
        self.assertEqual(machine_readable_bytes("987"), 987)
        self.assertEqual(machine_readable_bytes("987K"), 987000)
        self.assertEqual(machine_readable_bytes("987M"), 987000000)
        self.assertEqual(machine_readable_bytes("987G"), 987000000000)
        self.assertEqual(machine_readable_bytes("987T"), 987000000000000)
        self.assertEqual(machine_readable_bytes("987P"), 987000000000000000)
        self.assertEqual(machine_readable_bytes("987E"), 987000000000000000000)
        self.assertEqual(machine_readable_bytes("987k"), 987000)
        self.assertEqual(machine_readable_bytes("987m"), 987000000)
        self.assertEqual(machine_readable_bytes("987g"), 987000000000)
        self.assertEqual(machine_readable_bytes("987t"), 987000000000000)
        self.assertEqual(machine_readable_bytes("987p"), 987000000000000000)
        self.assertEqual(machine_readable_bytes("987e"), 987000000000000000000)

        self.assertRaises(ValueError, machine_readable_bytes, "987Z")


class TestRoundSizeToNearestBlock(MAASTestCase):
    def test_round_up_adds_extra_block(self):
        block_size = 4096
        size = block_size + 1
        self.assertEqual(
            2 * block_size,
            round_size_to_nearest_block(size, block_size, True),
            "Should add an extra block to the size.",
        )

    def test_round_up_doesnt_add_extra_block(self):
        block_size = 4096
        size = block_size
        self.assertEqual(
            size,
            round_size_to_nearest_block(size, block_size, True),
            "Shouldn't add an extra block to the size.",
        )

    def test_round_down_removes_block(self):
        block_size = 4096
        size = block_size + 1
        self.assertEqual(
            1 * block_size,
            round_size_to_nearest_block(size, block_size, False),
            "Should remove block from the size.",
        )

    def test_round_down_doesnt_remove_block(self):
        block_size = 4096
        size = block_size * 2
        self.assertEqual(
            size,
            round_size_to_nearest_block(size, block_size, False),
            "Shouldn't remove a block from the size.",
        )


class TestSystemdIntervalToCalendar(MAASTestCase):
    def test_every_2_hours(self):
        interval = "2h"
        self.assertEqual(
            "*-*-* 00/2:00:00", systemd_interval_to_calendar(interval)
        )

    def test_every_hour(self):
        interval = "1h"
        self.assertEqual(
            "*-*-* *:00:00", systemd_interval_to_calendar(interval)
        )

    def test_every_hour_and_a_half(self):
        interval = "1h 30m"
        self.assertEqual(
            "*-*-* *:00/30:00", systemd_interval_to_calendar(interval)
        )

    def test_every_30_minutes(self):
        interval = "30m"
        self.assertEqual(
            "*-*-* *:00/30:00", systemd_interval_to_calendar(interval)
        )

    def test_every_30_minutes_5_seconds(self):
        interval = "30m 5s"
        self.assertEqual(
            "*-*-* *:00/30:00/5", systemd_interval_to_calendar(interval)
        )

    def test_every_15_seconds(self):
        interval = "15s"
        self.assertEqual(
            "*-*-* *:*:00/15", systemd_interval_to_calendar(interval)
        )


GiB = 1024**3


class TestRoundSizeToNearestPowerOf2InGiB(MAASTestCase):
    def test_sub_gib_round_down_returns_zero(self):
        self.assertEqual(
            0, round_size_to_nearest_power_of_2_in_gib(512 * 1024**2, round_up=False)
        )

    def test_sub_gib_round_up_returns_two(self):
        self.assertEqual(
            2, round_size_to_nearest_power_of_2_in_gib(512 * 1024**2, round_up=True)
        )

    def test_zero_round_down_returns_zero(self):
        self.assertEqual(
            0, round_size_to_nearest_power_of_2_in_gib(0, round_up=False)
        )

    def test_exact_power_of_2_round_down(self):
        self.assertEqual(
            4, round_size_to_nearest_power_of_2_in_gib(4 * GiB, round_up=False)
        )

    def test_exact_power_of_2_round_up(self):
        self.assertEqual(
            4, round_size_to_nearest_power_of_2_in_gib(4 * GiB, round_up=True)
        )

    def test_non_power_of_2_round_down(self):
        # 10 GiB rounds down to 8
        self.assertEqual(
            8, round_size_to_nearest_power_of_2_in_gib(10 * GiB, round_up=False)
        )

    def test_non_power_of_2_round_up(self):
        # 10 GiB rounds up to 16
        self.assertEqual(
            16, round_size_to_nearest_power_of_2_in_gib(10 * GiB, round_up=True)
        )

    def test_1_gib_round_down(self):
        self.assertEqual(
            1, round_size_to_nearest_power_of_2_in_gib(1 * GiB, round_up=False)
        )

    def test_128_gib_round_down(self):
        self.assertEqual(
            128, round_size_to_nearest_power_of_2_in_gib(128 * GiB, round_up=False)
        )

    def test_1_tib_round_down(self):
        # 1024 GiB rounds down to 1024
        self.assertEqual(
            1024, round_size_to_nearest_power_of_2_in_gib(1024 * GiB, round_up=False)
        )
