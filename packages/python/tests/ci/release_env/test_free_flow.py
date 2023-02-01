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
        desc='master',
        config={},
        env_vars={'git_branch': 'refs/heads/master'},
        gh_res='master.json',
        release_env=ReleaseEnv(
            build_tag='master.b404',
            python_tag='rc0.dev404',
            is_release=False,
            is_release_pr=False,
            is_hotfix_pr=False,
            workflow=Workflow.free_flow,
        )
    ),
    TCase(
        desc='pr 1',
        config={},
        env_vars={'git_branch': 'refs/pull/1'},
        gh_res='pr1.json',
        release_env=ReleaseEnv(
            build_tag='pr1.b404',
            python_tag='b1.dev404',
            is_release=False,
            is_release_pr=False,
            is_hotfix_pr=False,
            workflow=Workflow.free_flow,
        )
    ),
    TCase(
        desc='local - uses a timestamp since git sha do not work with pip',
        config={},
        env_vars={'ci_env': False, 'run_id': ''},
        gh_res='master.json',  # not taken into account
        release_env=ReleaseEnv(
            build_tag='local.git-sha-abc-123',
            python_tag='a0+b123456789',
            is_release=False,
            is_release_pr=False,
            is_hotfix_pr=False,
            workflow=Workflow.free_flow,
        )
    ),
])
def test_m_flow(tcase: TCase, mocker: MockerFixture) -> None:
    config = CONFIG.copy(update=tcase.config)
    env_vars = ENV_VARS.copy(update=tcase.env_vars)

    config.workflow = Workflow.free_flow

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
