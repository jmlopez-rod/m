from io import StringIO

import sys
import pytest
from m.__main__ import main
from m.core import Bad, Good


def run_main(exit_value=0):
    prog = None
    with pytest.raises(SystemExit) as prog_block:
        prog = prog_block
        main()
    assert prog is not None and prog.value.code == exit_value


def test_m_npm_clean_tags(mocker):
    std_out = StringIO()
    mocker.patch.object(sys, 'argv', 'm npm clean_tags scope/pkg'.split(' '))
    mocker.patch.object(sys, 'stdout', std_out)
    mocker.patch('m.core.subprocess.eval_cmd').side_effect = [
        Good('{"tag1":"","tag2":"","tag3":"v3"}'),
        Good('- tag1'),
        Good('- tag2'),
    ]
    run_main()
    assert std_out.getvalue() == '["- tag1","- tag2"]\n'


def test_m_npm_clean_tags_fail(mocker):
    std_err = StringIO()
    mocker.patch.object(sys, 'argv', 'm npm clean_tags scope/pkg'.split(' '))
    mocker.patch.object(sys, 'stderr', std_err)
    mocker.patch('m.core.subprocess.eval_cmd').side_effect = [
        Good('{"tag1":"","tag2":"","tag3":"v3"}'),
        Good('- tag1'),
        Bad('some_error_tag2'),
    ]
    run_main(1)
    errors = std_err.getvalue()
    assert 'dist-tag rm issues' in errors
    assert 'some_error_tag2' in errors
    assert '- tag1' in errors
