from dataclasses import replace as copy
from typing import cast
from unittest.mock import patch

from m.ci.assert_branch import assert_branch
from m.ci.config import Config, GitFlowConfig, MFlowConfig, Workflow
from m.core.fp import Good

from m import git

from ..util import FpTestCase


class AssertBranchTest(FpTestCase):
    base_config = Config(
        'owner',
        'repo',
        '0.0.0',
        'm',
        Workflow.free_flow,
        GitFlowConfig(),
        MFlowConfig(),
    )

    @patch.object(git, 'get_branch')
    @patch('m.ci.assert_branch.read_config')
    def test_invalid_flow(self, read_config_mock, get_branch_mock):
        config = copy(self.base_config)
        config.workflow = cast(Workflow, 'oops')
        get_branch_mock.return_value = Good('master')
        read_config_mock.return_value = Good(config)
        res = assert_branch('release', 'm')
        self.assert_issue(res, 'invalid m workflow')

    @patch.object(git, 'get_branch')
    @patch('m.ci.assert_branch.read_config')
    def test_free_flow(self, read_config_mock, get_branch_mock):
        get_branch_mock.return_value = Good('master')
        read_config_mock.return_value = Good(self.base_config)
        res = assert_branch('release', 'm')
        self.assert_issue(
            res,
            'The free-flow workflow does not support releases',
        )

    @patch.object(git, 'get_branch')
    @patch('m.ci.assert_branch.read_config')
    def test_m_flow(self, read_config_mock, get_branch_mock):
        get_branch_mock.return_value = Good('master')
        config = copy(self.base_config)
        config.workflow = Workflow.m_flow
        read_config_mock.return_value = Good(config)
        res = assert_branch('release', 'm')
        self.assert_ok(res)
        res = assert_branch('hotfix', 'm')
        self.assert_ok(res)
        # different master branch
        config.m_flow = MFlowConfig('prod')
        get_branch_mock.return_value = Good('prod')
        res = assert_branch('release', 'm')
        self.assert_ok(res)

    @patch.object(git, 'get_branch')
    @patch('m.ci.assert_branch.read_config')
    def test_git_flow(self, read_config_mock, get_branch_mock):
        get_branch_mock.return_value = Good('develop')
        config = copy(self.base_config)
        config.workflow = Workflow.git_flow
        read_config_mock.return_value = Good(config)
        res = assert_branch('release', 'm')
        self.assert_ok(res)
        get_branch_mock.return_value = Good('master')
        res = assert_branch('hotfix', 'm')
        self.assert_ok(res)
        # different develop branch
        config.git_flow = GitFlowConfig('prod', 'dev')
        get_branch_mock.return_value = Good('dev')
        res = assert_branch('release', 'm')
        self.assert_ok(res)
        get_branch_mock.return_value = Good('prod')
        res = assert_branch('hotfix', 'm')
        self.assert_ok(res)

    @patch.object(git, 'get_branch')
    @patch('m.ci.assert_branch.read_config')
    def test_m_flow_error(self, read_config_mock, get_branch_mock):
        get_branch_mock.return_value = Good('topic/active-branch')
        config = copy(self.base_config)
        config.workflow = Workflow.m_flow
        read_config_mock.return_value = Good(config)
        res = assert_branch('release', 'm')
        self.assert_issue(
            res,
            "invalid branch for 'release' using m_flow",
        )
