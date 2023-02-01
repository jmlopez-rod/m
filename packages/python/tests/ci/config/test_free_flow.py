from typing import cast
from unittest.mock import patch

from m.ci.config import (
    Config,
    GitFlowConfig,
    MFlowConfig,
    Workflow,
    read_config,
    read_workflow,
)
from m.core import issue
from m.core.fp import Good
from m.core.issue import Issue

from ...util import FpTestCase


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

    def test_workflow_config(self):
        result = read_workflow('free-flow')
        workflow = self.assert_ok(result)
        self.assertEqual(workflow, Workflow.free_flow)

    def test_workflow_config_fail(self):
        result = read_workflow('unknown-flow')
        self.assert_issue(result, 'invalid workflow')

    @patch('m.core.json.read_json')
    def test_read_config_fail(self, read_json_mock):
        read_json_mock.return_value = issue('made up issue')
        result = read_config('m')
        self.assert_issue(result, 'read_config failure')

    def test_empty_config(self):
        with patch('m.core.json.read_json') as read_json_mock:
            read_json_mock.return_value = Good({})
            result = read_config('m')
            self.assert_issue(result, 'read_config failure')
            err = cast(Issue, cast(Issue, result.value).cause)
            self.assertEqual(err.message, 'multi_get key retrieval failure')
            if isinstance(err.context, list):
                msgs = {x['cause']['message'] for x in err.context}
                self.assertSetEqual(
                    msgs, set([
                        '`owner` path was not found',
                        '`repo` path was not found',
                    ]),
                )
            else:
                raise AssertionError('issue data should be a string')

    def test_pass(self):
        with patch('m.core.json.read_json') as read_json_mock:
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
