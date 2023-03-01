import json
import os
from datetime import datetime
from functools import partial

import pytest
from m.core import Good, issue
from m.core import rw as mio
from pytest_mock import MockerFixture
from tests.cli.conftest import assert_streams, run_cli

from .conftest import TCaseErr, get_fixture, read_file_fake

TODAY = datetime.now().strftime('%B %d, %Y')
env_mock = {'NO_COLOR': 'true'}


@pytest.mark.parametrize('tcase', [
    TCaseErr(
        cmd='m start_release',
        branch='topic/feature',
        exit_code=1,
        errors=[
            "invalid branch for 'release' using m_flow",
            '"requiredBranch": "master"',
        ],
    ),
    TCaseErr(
        cmd='m start_release',
        branch='master',
        status=('ahead', '-> msg'),
        exit_code=1,
        errors=[
            'branch is not in sync with the remote branch',
            '"suggestion": "try running `git pull`',
        ],
    ),
    TCaseErr(
        cmd='m start_release',
        branch='master',
        status=('behind', '<- msg'),
        exit_code=1,
        errors=[
            'branch is not in sync with the remote branch',
            '"suggestion": "try running `git pull`',
        ],
    ),
    TCaseErr(
        cmd='m start_release',
        branch='master',
        status=('dirty', 'cannot stash'),
        exit_code=1,
        errors=[
            'releases can only be done in a clean git state',
            '"git_status": "dirty"',
        ],
    ),
    TCaseErr(
        cmd='m start_release',
        branch='master',
        status=('dirty', 'Changes not staged'),
        user_input=['no'],
        exit_code=1,
        errors=[
            'releases can only be done in a clean git state',
            '"git_status": "dirty"',
        ],
    ),
    TCaseErr(
        cmd='m start_release',
        branch='master',
        status=('dirty', 'Changes not staged'),
        user_input=['yes'],
        git_stash=issue('oops, cannot help you here'),
        exit_code=1,
        errors=[
            'would you like to stash the changes and continue?',
            'git stash failure',
        ],
    ),
    TCaseErr(
        cmd='m start_release',
        branch='master',
        status=('dirty', 'Changes not staged'),
        user_input=['yes', 'no'],
        git_stash=Good('we stashed your changes'),
        commits=[],
        exit_code=1,
        errors=[
            'there are no commits to release',
            'Proceed with a release instead of a hotfix?',
            'release aborted by user',
            '"suggestion": "consider creating a hotfix"',
        ],
    ),
    TCaseErr(
        cmd='m start_release',
        branch='master',
        status=('clean', 'oh good for you'),
        user_input=['0.1.0'],
        commits=['feature 1', 'feature 2'],
        git_checkout=issue('unable to switch branches'),
        exit_code=1,
        errors=[
            'unable to switch branches',
        ],
    ),
    TCaseErr(
        cmd='m start_release',
        branch='master',
        status=('clean', 'oh good for you'),
        # no commits - should be a hotfix but we do it anyway
        user_input=['yes', '0.1.0'],
        commits=[],
        git_checkout=issue('unable to switch branches'),
        exit_code=1,
        errors=[
            'Proceed with a release instead of a hotfix?',
            'unable to switch branches',
        ],
    ),
    # hotfix version
    TCaseErr(
        cmd='m start_hotfix',
        branch='master',
        status=('clean', 'oh good for you'),
        # Commits may be features - proceeding anyway
        user_input=['yes', '0.1.0'],
        commits=['feature 1'],
        git_checkout=issue('unable to switch branches'),
        exit_code=1,
        errors=[
            'hotfix may contain unreleased features',
            'Disregard warning and proceed with hotfix?',
            'unable to switch branches',
        ],
    ),
    # hotfix version
    TCaseErr(
        cmd='m start_hotfix',
        branch='master',
        status=('clean', 'oh good for you'),
        # Commits may be features - stopping processes
        user_input=['no'],
        commits=['feature 1'],
        git_checkout=issue('unable to switch branches'),
        exit_code=1,
        errors=[
            'hotfix may contain unreleased features',
            'Disregard warning and proceed with hotfix?',
            'hotfix aborted by user',
            '"suggestion": "consider creating a release"',
        ],
    ),
    TCaseErr(
        cmd='m start_release',
        branch='master',
        status=('dirty', 'Changes not staged'),
        git_stash=Good('we stashed your changes'),
        git_stash_pop=issue('something went wrong popping the stash'),
        user_input=['yes', '0.1.0'],
        commits=['feature 1'],
        git_checkout=Good('switch to release branch'),
        exit_code=0,
        errors=[
            '`git stash pop` issue',
            'something went wrong popping the stash',
        ],
    ),
    TCaseErr(
        cmd='m start_release',
        branch='master',
        status=('dirty', 'Changes not staged'),
        git_stash=Good('we stashed your changes'),
        git_stash_pop=Good('your changes are back'),
        user_input=['yes', '0.1.0'],
        commits=['feature 1'],
        git_checkout=Good('switch to release branch'),
        exit_code=0,
        expected=get_fixture('release.log'),
    ),
])
def test_m_start_release_errors(mocker: MockerFixture, tcase: TCaseErr):
    # Checking output with json instead of yaml
    mocker.patch.dict(os.environ, env_mock, clear=True)
    mocker.patch('time.time').return_value = 123456789
    fake = partial(read_file_fake, f_map={
        'm/m.json': 'm.json',
        'CHANGELOG.md': 'cl_basic.md',
    })
    mocker.patch('builtins.input').side_effect = tcase.user_input
    mocker.patch.object(mio, 'read_file', fake)
    mocker.patch('m.git.get_branch').return_value = Good(tcase.branch)
    mocker.patch('m.git.get_status').return_value = Good(tcase.status)
    mocker.patch('m.git.checkout_branch').return_value = tcase.git_checkout
    ver = '0.0.1'
    mocker.patch('m.github.cli.get_latest_release').return_value = Good(ver)
    mocker.patch('m.git.get_commits').return_value = Good(tcase.commits)
    mocker.patch('m.git.stash').return_value = tcase.git_stash
    mocker.patch('m.git.stash_pop').return_value = tcase.git_stash_pop
    mocker.patch('m.git.get_first_commit_sha').return_value = Good('sha123abc')
    mocker.patch('m.core.rw.write_file').return_value = Good(None)
    mocker.patch('m.core.json.read_json').return_value = Good(
        json.loads(get_fixture('m.json')),
    )

    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
