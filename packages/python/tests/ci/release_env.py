import unittest
from unittest.mock import patch
from typing import cast

from m.core import one_of
from m.core.issue import Issue
from m.core.fp import Good
from m.ci.config import ReleaseFrom, Config
from m.core.io import EnvVars
from m.ci.git_env import get_git_env
from m.ci.release_env import get_release_env


def read_fixture(name: str) -> str:
    with open(f'packages/python/tests/ci/fixtures/{name}.json') as fp:
        return fp.read()


def mock_commit_sha(sha: str) -> str:
    return """{
        "data": {
            "repository": {
                "commit": {
                    "message": "Merge %s into sha2"
                }
            }
        }
    }""" % sha


class ReleaseEnvTest(unittest.TestCase):
    config = Config(
        owner='jmlopez-rod',
        repo='m',
        version='0.0.0',
        m_dir='m',
        release_from_dict=dict(
            master=ReleaseFrom(
                pr_branch='release',
                allowed_files=['m/m.json', 'CHANGELOG.md']
            )
        )
    )
    env_vars = EnvVars(
        ci_env=True,
        github_token='super_secret_like_damn',
        server_url='abc.xyz',
        run_id='404',
        run_number='1',
        run_url='http://abc.xyz/404',
        git_branch='refs/heads/master',
        git_sha='git-sha-abc-123',
    )

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
        result = self._get_env()
        self.assertFalse(result.is_bad)
        self.assertEqual(result.value.__dict__, dict(
            version='0.0.0-local.git-sha-abc-123',
            is_release=False,
            is_release_pr=False,
            release_from=self.config.release_from_dict['master'],
        ))

    def test_master_behind(self):
        """Github says version is 1.1.1 but the config is still in 0.0.0
        This can be fixed by merging the latest. This usually happens when a
        release gets merged and now the other branches are behind. So this
        type of error will be a good reminder to developers to update.
        """
        self.env_vars.ci_env = True
        self.config.version = '0.0.0'
        self.env_vars.git_branch = 'refs/heads/master'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('master')),
            ]
            result = self._get_env()
            self.assertTrue(result.is_bad)
            iss = cast(Issue, result.value)
            self.assertEqual(
                iss.message,
                'config version is behind (Branch may need to be updated)'
            )

    def test_master(self):
        self.env_vars.ci_env = True
        self.config.version = '1.1.1'
        self.env_vars.git_branch = 'refs/heads/master'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('master')),
            ]
            result = self._get_env()
            self.assertFalse(result.is_bad)
            self.assertEqual(result.value.__dict__, dict(
                version='0.0.0-master.b404',
                is_release=False,
                is_release_pr=False,
                release_from=self.config.release_from_dict['master'],
            ))

    def test_pr_1(self):
        self.env_vars.ci_env = True
        self.config.version = '1.1.1'
        self.env_vars.git_branch = 'refs/pull/1'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('pr1')),
            ]
            result = self._get_env()
            self.assertFalse(result.is_bad)
            self.assertEqual(result.value.__dict__, dict(
                version='0.0.0-pr1.b404',
                is_release=False,
                is_release_pr=False,
                release_from=self.config.release_from_dict['master'],
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
                Good(read_fixture('release-pr')),
            ]
            result = self._get_env()
            self.assertTrue(result.is_bad)
            self.assertEqual(
                result.value.message,
                'config version needs to be bumped'
            )

    def test_release_pr(self):
        """Make sure that the developer updates the version to be greater than
        the current one in github."""
        self.env_vars.ci_env = True
        self.config.version = '1.1.2'
        self.env_vars.git_branch = 'refs/pull/2'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('release-pr')),
            ]
            result = self._get_env()
            self.assertFalse(result.is_bad)
            self.assertEqual(result.value.__dict__, dict(
                version='0.0.0-pr2.b404',
                is_release=False,
                is_release_pr=True,
                release_from=self.config.release_from_dict['master'],
            ))

    def test_release_merge(self):
        """Should use the proper version number"""
        self.env_vars.ci_env = True
        self.config.version = '1.1.1'
        self.env_vars.git_branch = 'refs/heads/master'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('merge-release')),
            ]
            result = self._get_env()
            self.assertFalse(result.is_bad)
            self.assertEqual(result.value.__dict__, dict(
                version='1.1.1',
                is_release=True,
                is_release_pr=False,
                release_from=self.config.release_from_dict['master'],
            ))

    def test_release_pr_empty_allowed(self):
        """Empty allowed should allow you to commit any files."""
        self.env_vars.ci_env = True
        self.config.version = '1.1.2'
        self.config.release_from_dict['master'].allowed_files = []
        self.env_vars.git_branch = 'refs/pull/2'
        with patch('m.core.http.fetch') as graphql_mock:
            graphql_mock.side_effect = [
                Good(mock_commit_sha('sha')),
                Good(read_fixture('release-pr')),
            ]
            result = self._get_env()
            self.assertFalse(result.is_bad)
            self.assertEqual(result.value.__dict__, dict(
                version='0.0.0-pr2.b404',
                is_release=False,
                is_release_pr=True,
                release_from=self.config.release_from_dict['master'],
            ))
