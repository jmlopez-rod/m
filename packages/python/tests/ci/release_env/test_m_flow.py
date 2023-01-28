from unittest.mock import patch

from m.ci.config import Workflow
from m.ci.git_env import get_git_env
from m.ci.release_env import get_release_env
from m.core import one_of
from m.core.fp import Good

from ...util import FpTestCase, read_fixture
from .util import CONFIG, ENV_VARS, mock_commit_sha


class ReleaseEnvMFlowTest(FpTestCase):
    config = CONFIG.copy()
    env_vars = ENV_VARS.copy()

    def __init__(self, methodName):
        super().__init__(methodName)
        self.config.workflow = Workflow.m_flow

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
        self.assertFalse(result.is_bad)
        self.assertEqual(result.value.__dict__, dict(
            build_tag='0.0.0-local.git-sha-abc-123',
            is_release=False,
            is_release_pr=False,
            is_hotfix_pr=False,
            workflow=Workflow.m_flow
        ))

    def test_master_behind(self):
        """Github says version is 1.1.1 but the config is still in 0.0.0 This
        can be fixed by merging the latest.

        This usually happens when a release gets merged and now the
        other branches are behind. So this type of error will be a good
        reminder to developers to update.
        """
        self.env_vars.ci_env = True
        self.config.version = '0.0.0'
        self.env_vars.git_branch = 'refs/heads/master'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('master.json')),
            ]
            result = self._get_env()
            self.assert_issue(
                result,
                'version is behind (Branch may need to be updated)')

    def test_master(self):
        self.env_vars.ci_env = True
        self.config.version = '1.1.1'
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
                build_tag='0.0.0-master.b404',
                is_release=False,
                is_release_pr=False,
                is_hotfix_pr=False,
                workflow=Workflow.m_flow
            ))

    def test_pr_1(self):
        self.env_vars.ci_env = True
        self.config.version = '1.1.1'
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
                build_tag='0.0.0-pr1.b404',
                is_release=False,
                is_release_pr=False,
                is_hotfix_pr=False,
                workflow=Workflow.m_flow
            ))

    def test_pr_1_dev_versioning(self):
        self.env_vars.ci_env = True
        self.config.version = '1.1.1'
        self.config.build_tag_with_version = True
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
                build_tag='1.1.1-pr1.b404',
                is_release=False,
                is_release_pr=False,
                is_hotfix_pr=False,
                workflow=Workflow.m_flow
            ))

    def test_release_pr_no_update(self):
        """Make sure that the developer updates the version to be greater than
        the current one in github."""
        self.env_vars.ci_env = True
        self.config.version = '1.1.1'
        self.env_vars.git_branch = 'refs/pull/2'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('release-pr.json')),
            ]
            result = self._get_env()
            self.assert_issue(result, 'version needs to be bumped')

    def test_release_hotfix_pr_wrong_target(self):
        """Hotfix prs should be done to the master branch."""
        self.env_vars.ci_env = True
        self.config.version = '1.1.1'
        self.env_vars.git_branch = 'refs/pull/2'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('hotfix-pr-wrong-baseref.json')),
            ]
            result = self._get_env()
            self.assert_issue(result, 'invalid hotfix-pr')

    def test_release_pr(self):
        """Make sure that the developer updates the version to be greater than
        the current one in github."""
        self.env_vars.ci_env = True
        self.config.version = '1.1.2'
        self.env_vars.git_branch = 'refs/pull/2'
        self.env_vars.run_id = '404'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('release-pr.json')),
            ]
            result = self._get_env()
            self.assert_ok(result)
            self.assertEqual(result.value.__dict__, dict(
                build_tag='1.1.2-rc2.b404',
                is_release=False,
                is_release_pr=True,
                is_hotfix_pr=False,
                workflow=Workflow.m_flow
            ))

    def test_release_pr_wrong_target(self):
        """In case we make a release pr to the wrong target branch.
        This is also making sure that checking the target branch takes priority
        over the version bump checking.
        """
        self.env_vars.ci_env = True
        self.config.version = '1.1.1'
        self.env_vars.git_branch = 'refs/pull/2'
        self.env_vars.run_id = '404'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('release-pr-wrong-baseref.json')),
            ]
            result = self._get_env()
            self.assert_issue(result, 'invalid release-pr')

    def test_release_merge(self):
        """Should use the proper version number."""
        self.env_vars.ci_env = True
        self.config.version = '1.1.2'
        self.env_vars.git_branch = 'refs/heads/master'
        self.env_vars.run_id = '404'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('merge-release.json')),
            ]
            result = self._get_env()
            self.assert_ok(result)
            self.assertEqual(result.value.__dict__, dict(
                build_tag='1.1.2',
                is_release=True,
                is_release_pr=False,
                is_hotfix_pr=False,
                workflow=Workflow.m_flow
            ))

    def test_release_pr_empty_allowed(self):
        """Empty allowed should allow you to commit any files."""
        self.env_vars.ci_env = True
        self.config.version = '1.1.2'
        self.env_vars.git_branch = 'refs/pull/2'
        self.env_vars.run_id = '404'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('release-pr.json')),
            ]
            result = self._get_env()
            self.assert_ok(result)
            self.assertEqual(result.value.__dict__, dict(
                build_tag='1.1.2-rc2.b404',
                is_release=False,
                is_release_pr=True,
                is_hotfix_pr=False,
                workflow=Workflow.m_flow
            ))

    def test_hotfix_merge(self):
        """Should use the proper version number."""
        self.env_vars.ci_env = True
        self.config.version = '1.1.2'
        self.env_vars.git_branch = 'refs/heads/master'
        self.env_vars.run_id = '404'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('merge-hotfix.json')),
            ]
            result = self._get_env()
            self.assert_ok(result)
            self.assertEqual(result.value.__dict__, dict(
                build_tag='1.1.2',
                is_release=True,
                is_release_pr=False,
                is_hotfix_pr=False,
                workflow=Workflow.m_flow
            ))
