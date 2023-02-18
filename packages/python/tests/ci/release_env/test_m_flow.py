import pytest
from m.ci.config import Workflow
from m.ci.git_env import get_git_env
from m.ci.release_env import ReleaseEnv, get_release_env
from m.core import one_of
from m.core.fp import Good
from pytest_mock import MockerFixture
from tests.conftest import assert_issue, assert_ok
from tests.util import read_fixture

from .util import CONFIG, ENV_VARS, TCase, mock_commit_sha


@pytest.mark.parametrize('tcase', [
    TCase(
        desc='master behind - release got merged but we have not pulled',
        config={'version': '0.0.0'},
        env_vars={'git_branch': 'refs/heads/master'},
        gh_res='master.json',
        err='version is behind (Branch may need to be updated)',
    ),
    TCase(
        desc='master',
        config={'version': '1.1.1'},
        env_vars={'git_branch': 'refs/heads/master'},
        gh_res='master.json',
        release_env=ReleaseEnv(
            build_tag='0.0.0-master.b404',
            python_tag='0.0.0rc0.dev404',
            is_release=False,
            is_release_pr=False,
            is_hotfix_pr=False,
            workflow=Workflow.m_flow,
        ),
    ),
    TCase(
        desc='pr 1',
        config={'version': '1.1.1'},
        env_vars={'git_branch': 'refs/pull/1'},
        gh_res='pr1.json',
        release_env=ReleaseEnv(
            build_tag='0.0.0-pr1.b404',
            python_tag='0.0.0b1.dev404',
            is_release=False,
            is_release_pr=False,
            is_hotfix_pr=False,
            workflow=Workflow.m_flow,
        ),
    ),
    TCase(
        desc='pr 1 - dev versioning',
        config={'version': '1.1.1', 'build_tag_with_version': True},
        env_vars={'git_branch': 'refs/pull/1'},
        gh_res='pr1.json',
        release_env=ReleaseEnv(
            build_tag='1.1.1-pr1.b404',
            python_tag='1.1.1b1.dev404',
            is_release=False,
            is_release_pr=False,
            is_hotfix_pr=False,
            workflow=Workflow.m_flow,
        ),
    ),
    TCase(
        desc='release pr - no version update',
        config={'version': '1.1.1'},
        env_vars={'git_branch': 'refs/pulls/2'},
        gh_res='release-pr.json',
        err='version needs to be bumped',
    ),
    TCase(
        desc='hotfix pr - wrong target, branch target takes priority',
        config={'version': '1.1.1'},
        env_vars={'git_branch': 'refs/pulls/2'},
        gh_res='hotfix-pr-wrong-baseref.json',
        err='invalid hotfix-pr',
    ),
    TCase(
        desc='release pr - make sure version is bumped',
        config={'version': '1.1.2'},
        env_vars={'git_branch': 'refs/pull/2'},
        gh_res='release-pr.json',
        release_env=ReleaseEnv(
            build_tag='1.1.2-rc2.b404',
            python_tag='1.1.2rc2.dev404',
            is_release=False,
            is_release_pr=True,
            is_hotfix_pr=False,
            workflow=Workflow.m_flow,
        ),
    ),
    TCase(
        desc='release pr - wrong target, branch target takes priority',
        config={'version': '1.1.1'},
        env_vars={'git_branch': 'refs/pulls/2'},
        gh_res='release-pr-wrong-baseref.json',
        err='invalid release-pr',
    ),
    TCase(
        desc='release merge - user proper version',
        config={'version': '1.2.0'},
        env_vars={'git_branch': 'refs/heads/master'},
        gh_res='merge-release.json',
        release_env=ReleaseEnv(
            build_tag='1.2.0',
            python_tag='1.2.0',
            is_release=True,
            is_release_pr=False,
            is_hotfix_pr=False,
            workflow=Workflow.m_flow,
        ),
    ),
    TCase(
        desc='release pr',
        config={'version': '1.1.2'},
        env_vars={'git_branch': 'refs/pull/2'},
        gh_res='release-pr.json',
        release_env=ReleaseEnv(
            build_tag='1.1.2-rc2.b404',
            python_tag='1.1.2rc2.dev404',
            is_release=False,
            is_release_pr=True,
            is_hotfix_pr=False,
            workflow=Workflow.m_flow,
        ),
    ),
    TCase(
        desc='hotfix merge - use proper version number',
        config={'version': '1.1.2'},
        env_vars={'git_branch': 'refs/heads/master'},
        gh_res='merge-hotfix.json',
        release_env=ReleaseEnv(
            build_tag='1.1.2',
            python_tag='1.1.2',
            is_release=True,
            is_release_pr=False,
            is_hotfix_pr=False,
            workflow=Workflow.m_flow,
        ),
    ),
    TCase(
        desc='local - uses a timestamp since git sha do not work with pip',
        config={},
        env_vars={'ci_env': False, 'run_id': ''},
        gh_res='master.json',  # not taken into account
        release_env=ReleaseEnv(
            build_tag='0.0.0-local.git-sha-abc-123',
            python_tag='0.0.0a0+b123456789',
            is_release=False,
            is_release_pr=False,
            is_hotfix_pr=False,
            workflow=Workflow.m_flow,
        ),
    ),
])
def test_m_flow(tcase: TCase, mocker: MockerFixture) -> None:
    config = CONFIG.copy(update=tcase.config)
    env_vars = ENV_VARS.copy(update=tcase.env_vars)

    config.workflow = Workflow.m_flow

    mocker.patch('time.time').return_value = 123456789
    mocker.patch('m.core.http.fetch').side_effect = [
        Good(mock_commit_sha('sha')),
        Good(read_fixture(tcase.gh_res)),
    ]

    env_either = one_of(lambda: [
        release_env
        for git_env in get_git_env(config, env_vars)
        for release_env in get_release_env(config, env_vars, git_env)
    ])
    if tcase.release_env:
        env = assert_ok(env_either)
        assert env == tcase.release_env, tcase.desc
    if tcase.err:
        assert_issue(env_either, tcase.err)
