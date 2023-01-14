import sys
from inspect import cleandoc as cdoc
from io import StringIO

import pytest
from m.__main__ import main


def run_main(exit_value=0):
    prog = None
    with pytest.raises(SystemExit) as prog_block:
        prog = prog_block
        main()
    assert prog is not None and prog.value.code == exit_value


def test_m_json_error(mocker):
    std_err = StringIO()
    mocker.patch.object(sys, 'argv', ['m', 'json', 'oops'])
    mocker.patch.object(sys, 'stderr', std_err)

    run_main(2)
    errors = std_err.getvalue()
    assert 'failed to parse the json data' in errors
    assert 'json.decoder.JSONDecodeError:' in errors


def test_m_json_normal(mocker):
    std_out = StringIO()
    mocker.patch.object(sys, 'argv', ['m', 'json', '[]'])
    mocker.patch.object(sys, 'stdout', std_out)
    run_main()
    assert std_out.getvalue() == '[]\n'


def test_m_json_sort(mocker):
    std_out = StringIO()
    mocker.patch.object(sys, 'argv', [
        'm',
        'json',
        '--sort-keys',
        '{"c": 3, "z": 99, "a": 1}',
    ])
    mocker.patch.object(sys, 'stdout', std_out)
    run_main()
    expected = """
    {
      "a": 1,
      "c": 3,
      "z": 99
    }
    """
    assert std_out.getvalue() == f'{cdoc(expected)}\n'
