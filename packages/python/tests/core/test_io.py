import os
from unittest.mock import patch

from m.core.io import env, format_seconds, renv, renv_vars

from ..util import FpTestCase


def mockenv(**envvars):
    return patch.dict(os.environ, envvars)


class IoTest(FpTestCase):
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

    @mockenv(SOME_URL='m.io')
    def test_env(self):
        self.assertEqual(env('NOT_SET'), '')
        self.assertEqual(env('SOME_URL'), 'm.io')

    @mockenv(SOME_URL='m.io')
    def test_renv(self):
        self.assert_issue(renv('NOT_SET'), 'missing NOT_SET in env')
        val = self.assert_ok(renv('SOME_URL'))
        self.assertEqual(val, 'm.io')

    @mockenv(VAR_1='val1', VAR_2='val2')
    def test_renv_vars(self):
        self.assert_issue(
            renv_vars(['NOPE1', 'VAR_1', 'NOPE2']),
            'missing [NOPE1, NOPE2] in env',
        )
        val = self.assert_ok(renv_vars(['VAR_2', 'VAR_1']))
        self.assertEqual(val, ['val2', 'val1'])
