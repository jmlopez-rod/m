import json
import os
from datetime import datetime
from functools import partial

import pytest
from m.core import Good
from m.core import rw as mio
from pytest_mock import MockerFixture
from tests.cli.conftest import assert_streams, run_cli

from .conftest import TCase, get_fixture, read_file_fake

TODAY = datetime.now().strftime('%B %d, %Y')
env_mock = {'NO_COLOR': 'true'}


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd='m end_release',
        branch='topic/feature',
        exit_code=1,
        errors=[
            'end_release can only be done from a release/hotfix branch',
            '"expected": "release/x.y.z or hotfix/x.y.z"',
        ],
    ),
    TCase(
        cmd='m end_release',
        branch='release/0.1.0',
        exit_code=1,
        graphql_response='with_conflicts.json',
        errors=[
            'found conflicting prs',
            '"31": "https://github.com/jmlopez-rod/git-flow/pull/31"',
        ],
    ),
    TCase(
        cmd='m end_release',
        branch='release/0.1.0',
        exit_code=1,
        graphql_response='no_prs.json',
        errors=[
            'no prs associated with the release/hotfix branch',
        ],
    ),
    TCase(
        cmd='m end_release',
        branch='release/0.1.0',
        exit_code=0,
        graphql_response='single.json',
        merge_result=[
            Good({
                'sha': 'some_sha',
                'merged': True,
                'message': 'Pull Request successfully merged',
            }),
        ],
        expected=get_fixture('single.log'),
        cleandoc=False,
        new_line=False,
    ),
    TCase(
        cmd='m end_release',
        branch='release/0.0.2',
        exit_code=0,
        graphql_response='git_flow.json',
        merge_result=[
            Good({
                'sha': 'some_sha',
                'merged': True,
                'message': 'Pull Request successfully merged',
            }),
            Good({
                'sha': 'some_other_sha',
                'merged': True,
                'message': 'Pull Request successfully merged',
            }),
        ],
        expected=get_fixture('git_flow.log'),
        gh_latest=['0.0.1' for _ in range(0, 40)] + ['0.0.2'],
        cleandoc=False,
        new_line=False,
    ),
    TCase(
        cmd='m end_release',
        branch='release/0.0.2',
        exit_code=0,
        graphql_response='git_flow_first_merged.json',
        merge_result=[
            Good({
                'sha': 'some_other_sha',
                'merged': True,
                'message': 'Pull Request successfully merged',
            }),
        ],
        expected=get_fixture('git_flow_first_merged.log'),
        errors=[
            'master branch pr already merged/closed',
        ],
        gh_latest=['0.0.1' for _ in range(0, 7)] + ['0.0.2'],
        cleandoc=False,
        new_line=False,
    ),
    TCase(
        cmd='m end_release',
        branch='release/0.0.2',
        exit_code=0,
        graphql_response='git_flow_done.json',
        merge_result=[],
        errors=[
            'master branch pr already merged/closed',
            'develop branch pr already merged/closed',
        ],
    ),
])
def test_m_end_release(mocker: MockerFixture, tcase: TCase):
    # Checking output with json instead of yaml
    mocker.patch.dict(os.environ, env_mock, clear=True)
    mocker.patch('time.time').return_value = 123456789
    mocker.patch('time.sleep').return_value = ''
    fake = partial(read_file_fake, f_map={'m/m.json': 'm.json'})
    mocker.patch('m.core.json.read_json').return_value = Good(
        json.loads(get_fixture('m.json')),
    )
    mocker.patch.object(mio, 'read_file', fake)
    mocker.patch('builtins.input').side_effect = tcase.user_input
    mocker.patch('m.git.get_branch').return_value = Good(tcase.branch)
    if tcase.graphql_response:
        mocker.patch('m.github.graphql.api.request').return_value = Good(
            json.loads(get_fixture(tcase.graphql_response)),
        )

    if tcase.merge_result:
        mocker.patch(
            'm.ci.end_release.merge_pr',
        ).side_effect = tcase.merge_result
    mocker.patch(
        'm.ci.end_release.get_latest_release',
    ).side_effect = [Good(ver) for ver in tcase.gh_latest]

    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
