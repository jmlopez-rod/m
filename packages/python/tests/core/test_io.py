import unittest

from m.core.io import format_seconds


class IoTest(unittest.TestCase):
    def test_format_seconds(self):
        self.assertEqual(format_seconds(0), '0s')
        self.assertEqual(format_seconds(60), '1m')
        self.assertEqual(format_seconds(60.1), '1m:100ms')
        self.assertEqual(format_seconds(60.75), '1m:750ms')
        self.assertEqual(format_seconds(119.75), '1m:59s:750ms')
        self.assertEqual(format_seconds(65), '1m:5s')
        self.assertEqual(format_seconds(124), '2m:4s')
        self.assertEqual(format_seconds(3730), '1h:2m:10s')
        self.assertEqual(format_seconds(90061), '1d:1h:1m:1s')
        self.assertEqual(format_seconds(720488), '8d:8h:8m:8s')
