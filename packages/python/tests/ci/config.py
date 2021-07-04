import unittest
from unittest.mock import patch
from typing import cast

from m.core import issue
from m.core.issue import Issue
from m.core.fp import Good
from m.ci.config import read_config, Config


class ConfigTest(unittest.TestCase):
    def test_read_config_fail(self):
        with patch('m.core.json.read_json') as read_json_mock:
            read_json_mock.return_value = issue('made up issue')
            result = read_config('m')
            self.assertTrue(result.is_bad)
            err = cast(Issue, result.value)
            self.assertEqual(err.message, 'read_config failure')

    def test_empty_config(self):
        with patch('m.core.json.read_json') as read_json_mock:
            read_json_mock.return_value = Good({})
            result = read_config('m')
            self.assertTrue(result.is_bad)
            err = cast(Issue, cast(Issue, result.value).cause)
            self.assertEqual(err.message, 'multi_get key retrieval failure')
            if isinstance(err.data, list):
                msgs = {x['cause']['message'] for x in err.data}
                self.assertSetEqual(msgs, set([
                    '`owner` path was not found',
                    '`repo` path was not found',
                    '`version` path was not found',
                ]))
            else:
                raise AssertionError('issue data should be a string')

    def test_bad_release_from(self):
        with patch('m.core.json.read_json') as read_json_mock:
            read_json_mock.return_value = Good(dict(
                owner='jmlopez-rod',
                repo='m',
                version='0.0.0',
                releaseFrom=dict(
                    master={},
                    prod=dict(prBranch='releaseProd')
                ),
            ))
            result = read_config('m')
            self.assertTrue(result.is_bad)
            err = cast(Issue, cast(Issue, result.value).cause)
            missing = ', '.join([
                'master.prBranch',
                'master.allowedFiles',
                'prod.allowedFiles',
            ])
            self.assertEqual(
                err.message,
                f'missing [{missing}] in releaseFrom')

    def test_pass(self):
        with patch('m.core.json.read_json') as read_json_mock:
            read_json_mock.return_value = Good(dict(
                owner='jmlopez-rod',
                repo='m',
                version='0.0.0',
                releaseFrom=dict(
                    master=dict(
                        prBranch='release',
                        allowedFiles=['CHANGELOG.md']
                    ),
                ),
            ))
            result = read_config('m')
            self.assertFalse(result.is_bad)
            config = cast(Config, result.value)
            self.assertIsInstance(config, Config)
            self.assertEqual({**config.__dict__, **dict(
                owner='jmlopez-rod',
                repo='m',
                version='0.0.0',
                m_dir='m',
            )}, config.__dict__)
            self.assertEqual(
                config.release_from['master'].allowed_files,
                ['CHANGELOG.md']
            )
