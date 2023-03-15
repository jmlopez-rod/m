import json
import os
from datetime import datetime
from functools import partial

import pytest
from m.core import Good, issue
from m.core import rw as mio
from pytest_mock import MockerFixture
from tests.cli.conftest import assert_streams, run_cli

from .conftest import TCase, get_fixture, read_file_fake

TODAY = datetime.now().strftime('%B %d, %Y')
env_mock = {'NO_COLOR': 'true'}


@pytest.mark.parametrize('tcase', [
    TCase(
        branch='topic/feature',
        exit_code=1,
        errors=[
            'review_release can only be done from a release/hotfix branch',
            '"expected": "release/x.y.z or hotfix/x.y.z"',
        ],
    ),
    TCase(
        branch='release/0.1.0',
        exit_code=1,
        graphql_response='in_progress.json',
        errors=[
            'release is already in review',
            '"31": "https://github.com/jmlopez-rod/git-flow/pull/31"',
            '"32": "https://github.com/jmlopez-rod/git-flow/pull/32"',
        ],
    ),
    TCase(
        branch='release/0.1.0',
        exit_code=1,
        user_input=['no'],
        errors=[
            'operation cancelled by user',
        ],
    ),
    TCase(
        branch='release/0.1.0',
        exit_code=1,
        user_input=['yes'],
        create_prs=[
            issue('[mocked bad result 1]'),
            issue('[mocked bad result 2]'),
        ],
        errors=[
            'unable to create release pull request',
            '"message": "[mocked bad result 1]"',
            '"message": "no prs were created, inspect logs for hints"',
        ],
    ),
    TCase(
        branch='release/0.1.0',
        exit_code=0,
        user_input=['yes'],
        create_prs=[
            Good({'html_url': 'https://pr1-url.com'}),
        ],
        expected=get_fixture('m_flow.log'),
        cleandoc=False,
        new_line=False,
    ),
    TCase(
        branch='release/0.1.0',
        exit_code=0,
        m_file='m_git_flow.json',
        user_input=['yes'],
        create_prs=[
            Good({'html_url': 'https://pr1-url.com'}),
            Good({'html_url': 'https://pr2-url.com'}),
        ],
        expected=get_fixture('git_flow.log'),
        cleandoc=False,
        new_line=False,
        pr_body_has='0.0.1',
    ),
    TCase(
        branch='release/0.1.0',
        exit_code=0,
        m_file='m_git_flow.json',
        user_input=['yes'],
        create_prs=[
            issue('some issue creating backport pr'),
            Good({'html_url': 'https://pr2-url.com'}),
        ],
        errors=[
            'unable to create backport pull request',
        ],
        expected=get_fixture('git_flow_failed_pr.log'),
        cleandoc=False,
        new_line=False,
    ),
])
def test_m_review_release(mocker: MockerFixture, tcase: TCase):
    # Checking output with json instead of yaml
    mocker.patch.dict(os.environ, env_mock, clear=True)
    mocker.patch('time.time').return_value = 123456789
    fake = partial(read_file_fake, f_map={'m/m.json': tcase.m_file})
    mocker.patch('m.core.json.read_json').return_value = Good(
        json.loads(get_fixture(tcase.m_file)),
    )
    create_pr_mock = mocker.patch('m.ci.review_release.create_pr')
    create_pr_mock.side_effect = tcase.create_prs
    mocker.patch('builtins.input').side_effect = tcase.user_input
    mocker.patch.object(mio, 'read_file', fake)
    mocker.patch(
        'm.ci.review_release.get_latest_release',
    ).return_value = Good('0.0.1')
    mocker.patch('builtins.input').side_effect = tcase.user_input
    mocker.patch('m.git.commit').return_value = Good('[mocked git commit]')
    mocker.patch('m.git.push_branch').return_value = Good('[mocked git push]')
    mocker.patch('m.git.stage_all').return_value = Good('[mocked git add]')
    mocker.patch('m.git.raw_status').return_value = Good('[mocked git status]')
    mocker.patch('m.git.get_branch').return_value = Good(tcase.branch)
    if tcase.graphql_response:
        mocker.patch('m.github.graphql.api.request').return_value = Good(
            json.loads(get_fixture(tcase.graphql_response)),
        )
    mocker.patch(
        'm.ci.end_release.get_latest_release',
    ).side_effect = [Good(ver) for ver in tcase.gh_latest]

    # Tests are done using m.json
    mocker.patch('m.ci.config.get_m_filename').return_value = Good('m/m.json')

    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)

    if tcase.pr_body_has:
        url = 'https://github.com/gh_owner/gh_repo/compare/0.0.1...HEAD'
        assert url in create_pr_mock.call_args[0][3].body

    assert_streams(std_out, std_err, tcase)
