import unittest
from unittest.mock import patch
from typing import cast

from m.core import issue
from m.core.issue import Issue
from m.core.fp import Good
from m.ci.config import ReleaseFrom, Config
from m.core.io import EnvVars
from m.ci.git_env import get_git_env, GitEnv


class GitEnvTest(unittest.TestCase):
    config = Config(
        owner='jmlopez-rod',
        repo='m',
        version='0.0.0',
        m_dir='m',
        release_from_dict=dict(
            master=ReleaseFrom(
                pr_branch='release',
                allowed_files=['m/m.json', 'CHANGELOG.md'],
                required_files=[]
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

    def test_local(self):
        self.env_vars.ci_env = False
        result = get_git_env(self.config, self.env_vars)
        self.assertFalse(result.is_bad)
        self.assertDictEqual(
            result.value.__dict__,
            GitEnv(
                sha='git-sha-abc-123',
                branch='master',
                target_branch='master'
            ).__dict__)

    def test_read_git_env_fail(self):
        self.env_vars.ci_env = True
        with patch('m.github.api.graphql') as graphql_mock:
            graphql_mock.return_value = issue('made up issue')
            result = get_git_env(self.config, self.env_vars)
            self.assertTrue(result.is_bad)
            err = cast(Issue, result.value)
            self.assertEqual(err.message, 'git_env failure')
            self.assertIsNotNone(err.cause)
            self.assertEqual(err.cause.message, 'made up issue')

    def test_bad_github_response(self):
        self.env_vars.ci_env = True
        with patch('m.github.api.graphql') as graphql_mock:
            graphql_mock.side_effect = [Good({}), Good({})]
            result = get_git_env(self.config, self.env_vars)
            self.assertTrue(result.is_bad)
            err = cast(Issue, result.value)
            self.assertEqual(
                err.cause.message,
                '`repository` path was not found')

    def test_pass(self):
        self.env_vars.ci_env = True
        with patch('m.github.api.graphql') as graphql_mock:
            graphql_mock.side_effect = [
                Good(dict(
                    repository=dict(
                        commit=dict(
                            message='Merge sha1 into sha2'
                        )
                    ))),
                Good(dict(
                    repository=dict(
                        commit=dict(
                            oid='123456789',
                            message='commit message',
                        )
                    )
                ))]
            result = get_git_env(self.config, self.env_vars)
            self.assertFalse(result.is_bad)
