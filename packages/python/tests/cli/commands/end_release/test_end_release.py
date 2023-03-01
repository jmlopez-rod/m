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
])
def test_m_end_release(mocker: MockerFixture, tcase: TCase):
    # Checking output with json instead of yaml
    mocker.patch.dict(os.environ, env_mock, clear=True)
    mocker.patch('time.time').return_value = 123456789
    fake = partial(read_file_fake, f_map={'m/m.json': 'm.json'})
    mocker.patch.object(mio, 'read_file', fake)
    mocker.patch('builtins.input').side_effect = tcase.user_input
    mocker.patch('m.git.get_branch').return_value = Good(tcase.branch)
    ver = '0.0.1'
    if tcase.graphql_response:
        mocker.patch('m.github.graphql.api.request').return_value = Good(
            json.loads(get_fixture(tcase.graphql_response)),
        )
    mocker.patch('m.github.cli.get_latest_release').return_value = Good(ver)

    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
