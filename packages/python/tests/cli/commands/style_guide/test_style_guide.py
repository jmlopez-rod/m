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
        cmd='m style_guide inspect eslint_ui',
        exit_code=10,
        errors=[
            "invalid branch for 'release' using m_flow",
            '"requiredBranch": "master"',
        ],
    ),
])
def test_style_guide(mocker: MockerFixture, tcase: TCaseErr):
    # Checking output with json instead of yaml
    mocker.patch.dict(os.environ, env_mock, clear=True)
    mocker.patch('time.time').return_value = 123456789
    fake = partial(read_file_fake, f_map={
        'eslint_ui.yaml': 'eslint_ui.yaml',
        'CHANGELOG.md': 'cl_basic.md',
    })
    mocker.patch.object(mio, 'read_file', fake)
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
