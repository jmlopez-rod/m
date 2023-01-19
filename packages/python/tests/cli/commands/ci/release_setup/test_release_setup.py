import json
import sys
from functools import partial

import m.core.rw as mio
import pytest
from m.__main__ import main
from m.core import Good
from pytest_mock import MockerFixture

from .conftest import (
    TCase,
    TCaseErr,
    assert_err,
    assert_result,
    get_fixture,
    read_file_fake,
)


@pytest.mark.parametrize('tcase', [
    TCaseErr(
        exit_code=2,
        args=[],
        std_out='',
        std_err='the following arguments are required: m_dir, new_ver',
        changelog=None,
    ),
    TCaseErr(
        exit_code=1,
        std_out='error: \n\n',
        std_err='missing "Unreleased" link',
        args=['m', '1.2.3'],
        changelog='cl_invalid.md',
    ),
])
def test_err_cases(mocker: MockerFixture, capsys, tcase: TCaseErr):
    mocker.patch.object(sys, 'argv', ['m', 'ci', 'release_setup'] + tcase.args)
    mocker.patch('m.git.get_first_commit_sha').return_value = Good('sha123abc')
    fake = partial(read_file_fake, f_map={
        'm/m.json': 'm_comma.json',
        'CHANGELOG.md': tcase.changelog or 'not_set.file_ext',
    })
    mocker.patch.object(mio, 'read_file', fake)
    write_file_mock = mocker.patch('m.core.rw.write_file')
    write_file_mock.return_value = Good(None)

    fake = partial(read_file_fake, f_map={
        'm/m.json': 'm_comma.json',
        'CHANGELOG.md': tcase.changelog or 'not_set.file_ext',
    })
    mocker.patch.object(mio, 'read_file', fake)

    # t = importlib.import_module('m.ci.release_setup')
    # importlib.reload(t)
    prog: pytest.ExceptionInfo[SystemExit]
    with pytest.raises(SystemExit) as prog_block:
        prog = prog_block
        main()

    captured = capsys.readouterr()
    # so this happens and it shouldn't, sys.out should be clean
    assert captured.out == tcase.std_out
    assert_err(prog, captured.err, tcase)


@pytest.mark.parametrize('tcase', [
    TCase(
        delta_link='https://github.com/gh_owner/gh_repo/compare/0.0.1...HEAD',
        changelog='cl_valid.md',
        m_file='m_comma.json',
        diff_cl=[],
        diff_mf=[
            '--- before\n',
            '+++ after\n',
            '@@ -1,5 +1,5 @@\n',
            ' {\n',
            '   "owner": "gh_owner",\n',
            '-  "version": "0.0.1",\n',
            '+  "version": "1.2.3",\n',
            '   "repo": "gh_repo"\n',
            ' }\n',
        ],
    ),
])
def test_cases(mocker: MockerFixture, capsys, tcase: TCase):

    mocker.patch.object(sys, 'argv', ['m', 'ci', 'release_setup'] + tcase.args)
    mocker.patch('m.git.get_first_commit_sha').return_value = Good('sha123abc')
    # mocker.patch('m.core.io.read_file').side_effect = partial(
    #     read_file_fake,
    #     {
    #         'm/m.json': tcase.m_file,
    #         'CHANGELOG.md': tcase.changelog,
    #     },
    # )
    fake = partial(read_file_fake, f_map={
        'm/m.json': tcase.m_file,
        'CHANGELOG.md': tcase.changelog,
    })
    mocker.patch.object(mio, 'read_file', fake)
    mocker.patch('m.core.json.read_json').return_value = Good(
        json.loads(get_fixture(tcase.m_file)),
    )
    write_file_mock = mocker.patch('m.core.rw.write_file')
    write_file_mock.return_value = Good(None)

    captured = capsys.readouterr()
    assert captured.err == ''
    assert captured.out == ''

    # t = importlib.import_module('m.ci.release_setup')
    # importlib.reload(t)
    prog: pytest.ExceptionInfo[SystemExit]
    with pytest.raises(SystemExit) as prog_block:
        prog = prog_block
        print('before main:', tcase.changelog)
        main()

    print('after main...')
    captured = capsys.readouterr()

    print('out|||||:', captured.out)
    print('err|||||:', captured.err)
    print('---')
    # assert 1 == 0
    assert_result(prog, captured.out, write_file_mock, tcase)
