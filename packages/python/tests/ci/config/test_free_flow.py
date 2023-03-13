from typing import cast
from unittest.mock import patch

from m.ci.config import (
    Config,
    GitFlowConfig,
    MFlowConfig,
    Workflow,
    read_config,
)
from m.core import issue
from m.core.fp import Good
from m.core.issue import Issue

from ...util import FpTestCase

# Mocking Path.exists - yaml, yml, json
config_files_output = (False, False, True)


class ConfigFreeFlowTest(FpTestCase):
    """The base config should not change during the tests.

    The version will be ignored during the free-flow workflow.
    """
    base_config = Config(
        owner='jmlopez-rod',
        repo='m',
        version='0.0.0',
        m_dir='m',
        workflow=Workflow.free_flow,
        git_flow=GitFlowConfig(),
        m_flow=MFlowConfig(),
    )

    @patch('pathlib.Path.exists')
    def test_read_config_missing(self, path_exists_mock):
        path_exists_mock.side_effect = (False, False, False)
        confg_result = read_config('m')
        self.assert_issue(confg_result, 'read_config failure')
        assert 'm file not found' in str(confg_result.value)

    @patch('pathlib.Path.exists')
    @patch('m.core.yaml_fp.read_yson')
    def test_read_config_fail(self, read_json_mock, path_exists_mock):
        path_exists_mock.side_effect = config_files_output
        read_json_mock.return_value = issue('made up issue')
        result = read_config('m')
        self.assert_issue(result, 'read_config failure')

    @patch('pathlib.Path.exists')
    def test_empty_config(self, path_exists_mock):
        path_exists_mock.side_effect = config_files_output
        with patch('m.core.yaml_fp.read_yson') as read_json_mock:
            read_json_mock.return_value = Good({})
            result = read_config('m')
            self.assert_issue(result, 'read_config failure')
            err = cast(Issue, cast(Issue, result.value).cause)
            self.assertEqual(err.message, 'pydantic validation error')
            if err.cause:
                msgs = str(err.cause)
                assert '2 validation errors for Config' in msgs
                assert 'owner\n  field required' in msgs
                assert 'repo\n  field required' in msgs
            else:
                raise AssertionError('issue data should be a string')

    @patch('pathlib.Path.exists')
    def test_pass(self, path_exists_mock):
        path_exists_mock.side_effect = config_files_output
        with patch('m.core.yaml_fp.read_yson') as read_json_mock:
            read_json_mock.return_value = Good(
                dict(
                    owner='jmlopez-rod',
                    repo='m',
                ),
            )
            result = read_config('m')
            config = cast(Config, self.assert_ok(result))
            self.assertIsInstance(config, Config)
            self.assertEqual(
                {
                    **config.__dict__, **dict(
                        owner='jmlopez-rod',
                        repo='m',
                        version='0.0.0',
                        m_dir='m',
                    ),
                }, config.__dict__,
            )

    def test_verify_version(self):
        """On free-flow there are no releases."""
        config = self.base_config.copy()
        _test = config.verify_version
        gh_latest = ''
        self.assert_ok(_test(gh_latest, False, False))
        self.assert_ok(_test(gh_latest, True, False))
        self.assert_ok(_test(gh_latest, False, True))
