from unittest.mock import patch

from m.ci.config import Workflow
from m.ci.git_env import get_git_env
from m.ci.release_env import get_release_env
from m.core import one_of
from m.core.fp import Good

from ...util import FpTestCase, read_fixture
from .util import CONFIG, ENV_VARS, mock_commit_sha


class ReleaseEnvFreeFlowTest(FpTestCase):
    config = CONFIG.copy()
    env_vars = ENV_VARS.copy()

    def _get_env(self):
        return one_of(lambda: [
            release_env
            for git_env in get_git_env(self.config, self.env_vars)
            for release_env in get_release_env(
                self.config,
                self.env_vars,
                git_env
            )
        ])

    def test_local(self):
        self.env_vars.ci_env = False
        self.env_vars.run_id = ''
        result = self._get_env()
        self.assert_ok(result)
        self.assertEqual(result.value.__dict__, dict(
            build_tag='local.git-sha-abc-123',
            is_release=False,
            is_release_pr=False,
            is_hotfix_pr=False,
            workflow=Workflow.free_flow
        ))

    def test_master(self):
        self.env_vars.ci_env = True
        self.env_vars.git_branch = 'refs/heads/master'
        self.env_vars.run_id = '404'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('master.json')),
            ]
            result = self._get_env()
            self.assert_ok(result)
            self.assertEqual(result.value.__dict__, dict(
                build_tag='master.b404',
                is_release=False,
                is_release_pr=False,
                is_hotfix_pr=False,
                workflow=Workflow.free_flow
            ))

    def test_pr_1(self):
        self.env_vars.ci_env = True
        self.env_vars.git_branch = 'refs/pull/1'
        self.env_vars.run_id = '404'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('pr1.json')),
            ]
            result = self._get_env()
            self.assert_ok(result)
            self.assertEqual(result.value.__dict__, dict(
                build_tag='pr1.b404',
                is_release=False,
                is_release_pr=False,
                is_hotfix_pr=False,
                workflow=Workflow.free_flow
            ))
