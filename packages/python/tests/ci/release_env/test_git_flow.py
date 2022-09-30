from dataclasses import replace as copy
from unittest.mock import patch

from m.ci.config import Workflow
from m.ci.git_env import get_git_env
from m.ci.release_env import get_release_env
from m.core import one_of
from m.core.fp import Good

from ...util import FpTestCase, read_fixture
from .util import CONFIG, ENV_VARS, mock_commit_sha


class ReleaseEnvGitFlowTest(FpTestCase):
    config = copy(CONFIG)
    env_vars = copy(ENV_VARS)

    def __init__(self, methodName):
        super().__init__(methodName)
        self.config.workflow = Workflow.git_flow

    def _get_env(self):
        return one_of(
            lambda: [
                release_env
                for git_env in get_git_env(self.config, self.env_vars)
                for release_env in get_release_env(
                    self.config,
                    self.env_vars,
                    git_env,
                )
            ],
        )

    def test_branch_behind(self):
        """Github says version is 1.1.1 but the config is still in 0.0.0 This
        can be fixed by merging the latest.

        This usually happens when a release gets merged and now the
        other branches are behind. So this type of error will be a good
        reminder to developers to update.
        """
        self.env_vars.ci_env = True
        self.config.version = '0.0.0'
        self.env_vars.git_branch = 'refs/heads/my-branch'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('master.json')),
            ]
            result = self._get_env()
            self.assert_issue(
                result,
                'version is behind (Branch may need to be updated)',
            )

    def test_version_ahead(self):
        """Github says version is 1.1.1 but the config is in 2.0.0.

        This can be due to a mistake on a developer that bumped the
        version.
        """
        self.env_vars.ci_env = True
        self.config.version = '2.0.0'
        self.env_vars.git_branch = 'refs/heads/my-branch'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('master.json')),
            ]
            result = self._get_env()
            self.assert_issue(
                result,
                'version is ahead (Revert configuration change)',
            )

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
            self.assertEqual(
                result.value.__dict__, dict(
                    build_tag='999.0.0-master.b404',
                    is_release=False,
                    is_release_pr=False,
                    is_hotfix_pr=False,
                    workflow=Workflow.git_flow,
                ),
            )

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
            self.assertEqual(
                result.value.__dict__, dict(
                    build_tag='999.0.0-pr1.b404',
                    is_release=False,
                    is_release_pr=False,
                    is_hotfix_pr=False,
                    workflow=Workflow.git_flow,
                ),
            )

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

    def test_pr_release_no_update_develop(self):
        self.env_vars.ci_env = True
        self.config.version = '1.1.1'
        self.env_vars.git_branch = 'refs/pull/1'
        self.env_vars.run_id = '404'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('release-pr-develop.json')),
            ]
            result = self._get_env()
            self.assert_ok(result)
            self.assertEqual(
                result.value.__dict__, dict(
                    build_tag='SKIP',
                    is_release=False,
                    is_release_pr=True,
                    is_hotfix_pr=False,
                    workflow=Workflow.git_flow,
                ),
            )

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
            self.assertEqual(
                result.value.__dict__, dict(
                    build_tag='1.1.2-rc2.b404',
                    is_release=False,
                    is_release_pr=True,
                    is_hotfix_pr=False,
                    workflow=Workflow.git_flow,
                ),
            )

    def test_release_pr_develop(self):
        """Proper PR made to develop."""
        self.env_vars.ci_env = True
        self.config.version = '1.1.2'
        self.env_vars.git_branch = 'refs/pull/2'
        self.env_vars.run_id = '404'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('release-pr-develop.json')),
            ]
            result = self._get_env()
            self.assert_ok(result)
            self.assertEqual(
                result.value.__dict__, dict(
                    build_tag='SKIP',
                    is_release=False,
                    is_release_pr=True,
                    is_hotfix_pr=False,
                    workflow=Workflow.git_flow,
                ),
            )

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
            self.assertEqual(
                result.value.__dict__, dict(
                    build_tag='1.1.2',
                    is_release=True,
                    is_release_pr=False,
                    is_hotfix_pr=False,
                    workflow=Workflow.git_flow,
                ),
            )

    def test_release_merge_develop(self):
        """Need to merge release back into develop and make sure that the build
        passes."""
        self.env_vars.ci_env = True
        self.config.version = '1.1.1'
        self.env_vars.git_branch = 'refs/heads/develop'
        self.env_vars.run_id = '404'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('merge-release-develop.json')),
            ]
            result = self._get_env()
            self.assert_ok(result)
            self.assertEqual(
                result.value.__dict__, dict(
                    build_tag='999.0.0-develop.b404',
                    is_release=False,
                    is_release_pr=False,
                    is_hotfix_pr=False,
                    workflow=Workflow.git_flow,
                ),
            )

    def test_hotfix_pr_no_update(self):
        """Make sure that the developer updates the version to be greater than
        the current one in github."""
        self.env_vars.ci_env = True
        self.config.version = '1.1.1'
        self.env_vars.git_branch = 'refs/pull/2'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('hotfix-pr.json')),
            ]
            result = self._get_env()
            self.assert_issue(result, 'version needs to be bumped')

    def test_pr_hotfix_no_update_develop(self):
        self.env_vars.ci_env = True
        self.config.version = '1.1.1'
        self.env_vars.git_branch = 'refs/pull/1'
        self.env_vars.run_id = '404'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('hotfix-pr-develop.json')),
            ]
            result = self._get_env()
            self.assert_ok(result)
            self.assertEqual(
                result.value.__dict__, dict(
                    build_tag='SKIP',
                    is_release=False,
                    is_release_pr=False,
                    is_hotfix_pr=True,
                    workflow=Workflow.git_flow,
                ),
            )

    def test_hotfix_pr(self):
        """Make sure that the developer updates the version to be greater than
        the current one in github."""
        self.env_vars.ci_env = True
        self.config.version = '1.1.2'
        self.env_vars.git_branch = 'refs/pull/2'
        self.env_vars.run_id = '404'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('hotfix-pr.json')),
            ]
            result = self._get_env()
            self.assert_ok(result)
            self.assertEqual(
                result.value.__dict__, dict(
                    build_tag='1.1.2-hotfix2.b404',
                    is_release=False,
                    is_release_pr=False,
                    is_hotfix_pr=True,
                    workflow=Workflow.git_flow,
                ),
            )

    def test_hotfix_pr_develop(self):
        """Proper PR made to develop."""
        self.env_vars.ci_env = True
        self.config.version = '1.1.2'
        self.env_vars.git_branch = 'refs/pull/2'
        self.env_vars.run_id = '404'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('hotfix-pr-develop.json')),
            ]
            result = self._get_env()
            self.assert_ok(result)
            self.assertEqual(
                result.value.__dict__, dict(
                    build_tag='SKIP',
                    is_release=False,
                    is_release_pr=False,
                    is_hotfix_pr=True,
                    workflow=Workflow.git_flow,
                ),
            )

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
            self.assertEqual(
                result.value.__dict__, dict(
                    build_tag='1.1.2',
                    is_release=True,
                    is_release_pr=False,
                    is_hotfix_pr=False,
                    workflow=Workflow.git_flow,
                ),
            )

    def test_hotfix_merge_develop(self):
        """Should build since we need to make sure potential fixes done in
        hotfix are going to work with the current develop.

        At this point the configuration version should be the same as in
        github.
        """
        self.env_vars.ci_env = True
        self.config.version = '1.1.1'
        self.env_vars.git_branch = 'refs/heads/develop'
        self.env_vars.run_id = '404'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('merge-hotfix-develop.json')),
            ]
            result = self._get_env()
            self.assert_ok(result)
            self.assertEqual(
                result.value.__dict__, dict(
                    build_tag='999.0.0-develop.b404',
                    is_release=False,
                    is_release_pr=False,
                    is_hotfix_pr=False,
                    workflow=Workflow.git_flow,
                ),
            )

    def test_hotfix_merge_random(self):
        """We should not be merging hotfix branches to random branches."""
        self.env_vars.ci_env = True
        self.config.version = '1.1.2'
        self.env_vars.git_branch = 'refs/heads/random'
        self.env_vars.run_id = '404'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('merge-hotfix-random.json')),
            ]
            result = self._get_env()
            self.assert_issue(
                result,
                'version is ahead (Revert configuration change)',
            )
