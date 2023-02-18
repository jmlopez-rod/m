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
        desc='tracking other random branch',
        config={'version': '1.1.1'},
        env_vars={'git_branch': 'refs/heads/random'},
        gh_res='master.json',  # we can copy file but it would be the same
        release_env=ReleaseEnv(
            build_tag='0.0.0-random.b404',
            python_tag='0.0.0a0.dev404',
            is_release=False,
            is_release_pr=False,
            is_hotfix_pr=False,
            workflow=Workflow.git_flow,
        ),
    ),
    TCase(
        desc='master branch',
        config={'version': '1.1.1'},
        env_vars={'git_branch': 'refs/heads/master'},
        gh_res='master.json',
        release_env=ReleaseEnv(
            build_tag='0.0.0-master.b404',
            python_tag='0.0.0rc0.dev404',
            is_release=False,
            is_release_pr=False,
            is_hotfix_pr=False,
            workflow=Workflow.git_flow,
        ),
    ),
    TCase(
        desc='pull request 1',
        config={'version': '1.1.1'},
        env_vars={'git_branch': 'refs/pull/1'},
        gh_res='pr1.json',
        release_env=ReleaseEnv(
            build_tag='0.0.0-pr1.b404',
            python_tag='0.0.0b1.dev404',
            is_release=False,
            is_release_pr=False,
            is_hotfix_pr=False,
            workflow=Workflow.git_flow,
        ),
    ),
    TCase(
        desc='release pr no update develop',
        config={'version': '1.1.1'},
        env_vars={'git_branch': 'refs/pull/1'},
        gh_res='release-pr-develop.json',
        release_env=ReleaseEnv(
            build_tag='SKIP',
            python_tag='SKIP',
            is_release=False,
            is_release_pr=True,
            is_hotfix_pr=False,
            workflow=Workflow.git_flow,
        ),
    ),
    TCase(
        desc='release pull request',
        config={'version': '1.1.2'},
        env_vars={'git_branch': 'refs/pull/2'},
        gh_res='release-pr.json',
        release_env=ReleaseEnv(
            build_tag='1.1.2-rc2.b404',
            python_tag='1.1.2rc2.dev404',
            is_release=False,
            is_release_pr=True,
            is_hotfix_pr=False,
            workflow=Workflow.git_flow,
        ),
    ),
    TCase(
        desc='release pr develop',
        config={'version': '1.1.2'},
        env_vars={'git_branch': 'refs/pull/2'},
        gh_res='release-pr-develop.json',
        release_env=ReleaseEnv(
            build_tag='SKIP',
            python_tag='SKIP',
            is_release=False,
            is_release_pr=True,
            is_hotfix_pr=False,
            workflow=Workflow.git_flow,
        ),
    ),
    TCase(
        desc='release merge - use proper version number',
        config={'version': '1.1.2'},
        env_vars={'git_branch': 'refs/heads/master'},
        gh_res='merge-release.json',
        release_env=ReleaseEnv(
            build_tag='1.1.2',
            python_tag='1.1.2',
            is_release=True,
            is_release_pr=False,
            is_hotfix_pr=False,
            workflow=Workflow.git_flow,
        ),
    ),
    TCase(
        desc='release merge develop - need to merge back to develop branch',
        config={'version': '1.1.1'},
        env_vars={'git_branch': 'refs/heads/develop'},
        gh_res='merge-release-develop.json',
        release_env=ReleaseEnv(
            build_tag='0.0.0-develop.b404',
            python_tag='0.0.0b0.dev404',
            is_release=False,
            is_release_pr=False,
            is_hotfix_pr=False,
            workflow=Workflow.git_flow,
        ),
    ),
    TCase(
        desc='pr hotfix no update develop',
        config={'version': '1.1.1'},
        env_vars={'git_branch': 'refs/pull/1'},
        gh_res='hotfix-pr-develop.json',
        release_env=ReleaseEnv(
            build_tag='SKIP',
            python_tag='SKIP',
            is_release=False,
            is_release_pr=False,
            is_hotfix_pr=True,
            workflow=Workflow.git_flow,
        ),
    ),
    TCase(
        desc='pr hotfix develop - proper pr to develop',
        config={'version': '1.1.2'},
        env_vars={'git_branch': 'refs/pull/2'},
        gh_res='hotfix-pr-develop.json',
        release_env=ReleaseEnv(
            build_tag='SKIP',
            python_tag='SKIP',
            is_release=False,
            is_release_pr=False,
            is_hotfix_pr=True,
            workflow=Workflow.git_flow,
        ),
    ),
    TCase(
        desc='pr hotfix - version needs to be greater than the one in gh.',
        config={'version': '1.1.2'},
        env_vars={'git_branch': 'refs/pull/2'},
        gh_res='hotfix-pr.json',
        release_env=ReleaseEnv(
            build_tag='1.1.2-hotfix2.b404',
            python_tag='1.1.2rc2.dev404',
            is_release=False,
            is_release_pr=False,
            is_hotfix_pr=True,
            workflow=Workflow.git_flow,
        ),
    ),
    TCase(
        desc='hotfix merge - user proper version.',
        config={'version': '1.1.2'},
        env_vars={'git_branch': 'refs/heads/master'},
        gh_res='merge-hotfix.json',
        release_env=ReleaseEnv(
            build_tag='1.1.2',
            python_tag='1.1.2',
            is_release=True,
            is_release_pr=False,
            is_hotfix_pr=False,
            workflow=Workflow.git_flow,
        ),
    ),
    TCase(
        # making sure potential fixes done in hotfix work in develop.
        desc='hotfix merge develop - config version should be the same as gh.',
        config={'version': '1.1.1'},
        env_vars={'git_branch': 'refs/heads/develop'},
        gh_res='merge-hotfix-develop.json',
        release_env=ReleaseEnv(
            build_tag='0.0.0-develop.b404',
            python_tag='0.0.0b0.dev404',
            is_release=False,
            is_release_pr=False,
            is_hotfix_pr=False,
            workflow=Workflow.git_flow,
        ),
    ),
    TCase(
        desc='branch behind - developer needs to merge the latest',
        config={'version': '0.0.0'},
        env_vars={'git_branch': 'refs/heads/my-branch'},
        gh_res='master.json',
        err='version is behind (Branch may need to be updated)',
    ),
    TCase(
        desc='version ahead - developer made a mistake and bumped?',
        config={'version': '2.0.0'},
        env_vars={'git_branch': 'refs/heads/my-branch'},
        gh_res='master.json',
        err='version is ahead (Revert configuration change)',
    ),
    TCase(
        desc='release pr - no update on version',
        config={'version': '1.1.1'},
        env_vars={'git_branch': 'refs/pull/2'},
        gh_res='release-pr.json',
        err='version needs to be bumped',
    ),
    TCase(
        desc='release pr - wrong target',
        config={'version': '1.1.1'},
        env_vars={'git_branch': 'refs/pull/2'},
        gh_res='release-pr-wrong-baseref.json',
        err='invalid release-pr',
    ),
    TCase(
        desc='hotfix pr - no update',
        config={'version': '1.1.1'},
        env_vars={'git_branch': 'refs/pull/2'},
        gh_res='hotfix-pr.json',
        err='version needs to be bumped',
    ),
    TCase(
        desc='hotfix pr - wrong target',
        config={'version': '1.1.1'},
        env_vars={'git_branch': 'refs/pull/2'},
        gh_res='hotfix-pr-wrong-baseref.json',
        err='invalid hotfix-pr',
    ),
    TCase(
        # too late, went ahead and merged it, no release was actually made
        desc='hotfix merge - merge random',
        config={'version': '1.1.2'},
        env_vars={'git_branch': 'refs/heads/random'},
        gh_res='merge-hotfix-random.json',
        err='version is ahead (Revert configuration change)',
    ),
])
def test_git_flow(tcase: TCase, mocker: MockerFixture) -> None:
    config = CONFIG.copy(update=tcase.config)
    env_vars = ENV_VARS.copy(update=tcase.env_vars)

    config.workflow = Workflow.git_flow
    env_vars.ci_env = True

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
