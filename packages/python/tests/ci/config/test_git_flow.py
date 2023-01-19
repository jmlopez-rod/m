from typing import cast
from unittest.mock import patch

from m.ci.config import (
    Config,
    GitFlowConfig,
    MFlowConfig,
    Workflow,
    read_config,
)
from m.core.fp import Good

from ...util import FpTestCase


class ConfigGitFlowTest(FpTestCase):
    base_config = Config(
        owner='jmlopez-rod',
        repo='m',
        version='0.0.0',
        m_dir='m',
        workflow=Workflow.git_flow,
        git_flow=GitFlowConfig(),
        m_flow=MFlowConfig(),
    )

    def test_pass(self):
        with patch('m.core.json.read_json') as read_json_mock:
            read_json_mock.return_value = Good(
                dict(
                    owner='jmlopez-rod',
                    repo='m',
                    version='0.0.0',
                    workflow='git_flow',
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
                        workflow=Workflow.git_flow,
                    ),
                }, config.__dict__,
            )

    def test_verify_version(self):
        """Test is already covered by the m_flow tests."""
        config = self.base_config.copy()
        self.assertEqual(config.workflow, Workflow.git_flow)
