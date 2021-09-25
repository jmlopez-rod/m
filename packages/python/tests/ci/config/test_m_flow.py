from dataclasses import replace as copy
from typing import cast
from unittest.mock import patch

from m.ci.config import (Config, GitFlowConfig, MFlowConfig, Workflow,
                         read_config)
from m.core.fp import Good

from ...util import FpTestCase


class ConfigMFlowTest(FpTestCase):
    base_config = Config(
        owner='jmlopez-rod',
        repo='m',
        version='0.0.0',
        m_dir='m',
        workflow=Workflow.M_FLOW,
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
                    workflow='m_flow',
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
                        workflow=Workflow.M_FLOW,
                    ),
                }, config.__dict__,
            )

    def test_verify_version(self):
        config = copy(self.base_config)
        _test = config.verify_version
        # Init Repo
        config.version = '0.0.0'
        gh_latest = ''
        self.assert_ok(_test(gh_latest, False, False))
        self.assert_ok(_test(gh_latest, True, False))
        self.assert_ok(_test(gh_latest, False, True))
        # No change in version
        config.version = '1.0.0'
        gh_latest = '1.0.0'
        self.assert_ok(_test(gh_latest, False, False))
        self.assert_issue(
            _test(gh_latest, True, False),
            'version needs to be bumped',
        )
        self.assert_issue(
            _test(gh_latest, False, True),
            'version was not bumped during release pr',
        )
        # Bumped version
        config.version = '1.1.0'
        gh_latest = '1.0.0'
        self.assert_issue(
            _test(gh_latest, False, False),
            'version is ahead (Revert configuration change)',
        )
        self.assert_ok(_test(gh_latest, True, False))
        self.assert_ok(_test(gh_latest, False, True))
        # Decreased version
        config.version = '0.0.9'
        gh_latest = '1.0.0'
        self.assert_issue(
            _test(gh_latest, False, False),
            'version is behind (Branch may need to be updated)',
        )
        self.assert_issue(
            _test(gh_latest, True, False),
            'version needs to be bumped',
        )
        self.assert_issue(
            _test(gh_latest, False, True),
            'version was not bumped during release pr',
        )
        # WTF?
        config.version = '0.0.9-pr123'
        gh_latest = '1.0.0'
        self.assert_issue(
            _test(gh_latest, False, True),
            'error comparing versions',
        )
