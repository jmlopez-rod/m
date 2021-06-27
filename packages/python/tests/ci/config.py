import unittest
from unittest.mock import patch
from typing import cast


class ConfigTest(unittest.TestCase):
    def test_read_config_fail(self):
        with patch('m.core.json.read_json') as read_json_mock:
            # pylint: disable=C0415
            from m.ci.config import read_config
            from m.core.issue import Issue, issue

            read_json_mock.return_value = issue('made up issue')
            result = read_config('unknown')
            self.assertTrue(result.is_bad)
            err = cast(Issue, result.value)
            self.assertEqual(err.message, 'made up issue')
