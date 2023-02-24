import os
from contextlib import suppress

import pytest
from m.core import Issue
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase, assert_streams, run_cli


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd='m jsonq merged',
        expected='true',
        std_in='{"merged":true}',
    ),
    TCase(
        cmd='m jsonq @- hotdog',
        expected='100',
        std_in='{"hotdog":100}',
    ),
    TCase(
        cmd='m jsonq [1] 0',
        expected='1',
    ),
    TCase(
        cmd=[
            'm',
            'jsonq',
            '{"a":{"b":{"c":["hello"] } } }',
            'a.b.c.0',
        ],
        expected='hello',
    ),
    TCase(
        cmd=[
            'm',
            'jsonq',
            '{"a":{"b":{"c":["hello"] } } }',
            'a.b.d.0',
        ],
        errors=[
            'multi_get key retrieval failure',
            'key lookup failure: `a.b.d.0`',
        ],
        exit_code=1,
    ),
    TCase(
        cmd=[
            'm',
            'jsonq',
            '{"a":{"b":{"c":["hello"] } } }',
            'a.b.c.1',
        ],
        errors=[
            'multi_get key retrieval failure',
            '`a.b.c` is not a dict',
        ],
        exit_code=1,
    ),
    TCase(
        cmd=[
            'm',
            'jsonq',
            '--warn',
            '{"a":{"b":{"c":["hello"] } } }',
            'a.b.c.1',
        ],
        exit_code=1,
        errors=['[WARNING]'],
    ),
    TCase(
        cmd=[
            'm',
            'jsonq',
            '[null, true, false, { }]',
            '0',
            '1',
            '3',
        ],
        expected='null\ntrue\n{}',
    ),
])
def test_m_jsonq(tcase: TCase, mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, {}, clear=True)
    if tcase.std_in:
        stdin_read = mocker.patch('sys.stdin.read')
        stdin_read.return_value = tcase.std_in
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)


def test_m_jsonq_json_traceback(mocker: MockerFixture) -> None:
    mocker.patch.dict(
        os.environ,
        {'DEBUG': 'true', 'NO_COLOR': 'true'},
        clear=True,
    )
    cmd = [
        'm',
        'jsonq',
        '{"a":0}',
        'b',
    ]
    _, std_err = run_cli(cmd, 1, mocker)
    # making sure we get json strings in the payload
    assert '"message": "key lookup failure: `b`"' in std_err


def test_m_jsonq_yaml_traceback(mocker: MockerFixture) -> None:
    mocker.patch.dict(
        os.environ,
        {'DEBUG': 'true', 'NO_COLOR': 'true'},
        clear=True,
    )
    cmd = [
        'm',
        'jsonq',
        '{"a":0}',
        'b',
    ]
    Issue.yaml_traceback = True
    std_err = ''
    with suppress(BaseException):
        _, std_err = run_cli(cmd, 1, mocker)
    Issue.yaml_traceback = False
    assert "- message: 'key lookup failure: `b`'" in std_err
