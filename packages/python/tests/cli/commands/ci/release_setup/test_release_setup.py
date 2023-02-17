import json
from datetime import datetime
from functools import partial

import pytest
from m.core import Good
from m.core import rw as mio
from pytest_mock import MockerFixture
from tests.cli.conftest import assert_streams, run_cli

from .conftest import (
    TCase,
    TCaseErr,
    assert_result,
    get_fixture,
    read_file_fake,
)

TODAY = datetime.now().strftime('%B %d, %Y')


@pytest.mark.parametrize('tcase', [
    TCaseErr(
        cmd='m ci release_setup',
        exit_code=2,
        errors=['the following arguments are required: m_dir, new_ver'],
        changelog=None,
    ),
    TCaseErr(
        cmd='m ci release_setup m 1.2.3',
        exit_code=1,
        errors=['missing "Unreleased" link'],
        changelog='cl_invalid.md',
    ),
])
def test_m_ci_release_setup_errors(mocker: MockerFixture, tcase: TCaseErr):
    fake = partial(read_file_fake, f_map={
        'm/m.json': 'm_comma.json',
        'CHANGELOG.md': tcase.changelog or 'not_set.file_ext',
    })
    mocker.patch.object(mio, 'read_file', fake)
    mocker.patch('m.git.get_first_commit_sha').return_value = Good('sha123abc')
    mocker.patch('m.core.rw.write_file').return_value = Good(None)

    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd='m ci release_setup m 1.2.3',
        delta_link='https://github.com/gh_owner/gh_repo/compare/0.0.1...HEAD',
        changelog='cl_valid.md',
        diff_cl=[
            '--- before\n',
            '+++ after\n',
            '@@ -1,3 +1,9 @@\n',
            ' # some changelog title\n',
            ' \n',
            ' ## [Unreleased]\n',
            '+\n',
            f'+## [1.2.3] <a name="1.2.3" href="#1.2.3">-</a> {TODAY}\n',
            '+\n',
            '+\n',
            '+[unreleased]: https://github.com/gh_owner/gh_repo/compare/1.2.3...HEAD\n',
            '+[1.2.3]: https://github.com/gh_owner/gh_repo/compare/sha123abc...1.2.3\n',
        ],
        m_file='m_comma.json',
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
    TCase(
        cmd='m ci release_setup m 1.2.3',
        delta_link='https://github.com/gh_owner/gh_repo/compare/0.0.1...HEAD',
        changelog='cl_basic.md',
        diff_cl=[
            '--- before\n',
            '+++ after\n',
            '@@ -4,8 +4,16 @@\n',
            ' \n',
            ' ## [Unreleased]\n',
            ' \n',
            f'+## [1.2.3] <a name="1.2.3" href="#1.2.3">-</a> {TODAY}\n',
            '+\n',
            '+\n',
            '+\n',
            ' ## [0.2.0] <a name="0.2.0" href="#0.2.0">-</a> August 25, 2021\n',
            ' desc 0.2\n',
            ' \n',
            ' ## [0.1.0] <a name="0.1.0" href="#0.1.0">-</a> August 21, 2021\n',
            ' desc 0.1\n',
            '+[unreleased]: https://github.com/gh_owner/gh_repo/compare/1.2.3...HEAD\n',
            '+[1.2.3]: https://github.com/gh_owner/gh_repo/compare/0.2.0...1.2.3\n',
            '+[0.2.0]: https://github.com/gh_owner/gh_repo/compare/0.1.0...0.2.0\n',
            '+[0.1.0]: https://github.com/gh_owner/gh_repo/compare/sha123abc...0.1.0\n',
        ],
        m_file='m_no_comma.json',
        diff_mf=[
            '--- before\n',
            '+++ after\n',
            '@@ -1,5 +1,5 @@\n',
            ' {\n',
            '   "owner": "gh_owner",\n',
            '   "repo": "gh_repo",\n',
            '-  "version": "0.0.1"\n',
            '+  "version": "1.2.3"\n',
            ' }\n',
        ],
    ),
])
def test_m_ci_release_setup(mocker: MockerFixture, tcase: TCase):
    fake = partial(read_file_fake, f_map={
        'm/m.json': tcase.m_file,
        'CHANGELOG.md': tcase.changelog,
    })
    mocker.patch.object(mio, 'read_file', fake)
    mocker.patch('m.git.get_first_commit_sha').return_value = Good('sha123abc')
    mocker.patch('m.core.json.read_json').return_value = Good(
        json.loads(get_fixture(tcase.m_file)),
    )
    write_file_mock = mocker.patch('m.core.rw.write_file')
    write_file_mock.return_value = Good(None)

    std_out, _ = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_result(std_out, write_file_mock, tcase)
