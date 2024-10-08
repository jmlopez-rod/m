from typing import Any

import pytest
from m.core import Bad, Good, Issue
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase as CliTestCase
from tests.cli.conftest import assert_streams, run_cli


class TCase(CliTestCase):
    """Test case for `m npm clean_tags`."""

    eval_cmd_side_effects: list[Any]  # list[OneOf[Issue, str]]


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd='m npm clean_tags scope/pkg',
        eval_cmd_side_effects=[
            Good('{"tag1":"","tag2":"","tag3":"v3"}'),
            Good('- tag1'),
            Good('- tag2'),
        ],
        expected='["- tag1","- tag2"]',
    ),
    TCase(
        cmd='m npm add_tags --branch default_branch scope/pkg 0.0.0-rc123.b123',
        eval_cmd_side_effects=[
            Good('+ next'),
            Good('+ pr123'),
        ],
        expected='["+ next","+ pr123"]',
    ),
    TCase(
        cmd='m npm add_tags --branch default_branch scope/pkg 1.1.1',
        eval_cmd_side_effects=[
            Good('+ latest'),
            Good('+ default_branch'),
        ],
        expected='["+ latest","+ default_branch"]',
    ),
    TCase(
        cmd='m npm add_tags --branch default_branch scope/pkg 0.0.0-pr12.b123',
        eval_cmd_side_effects=[
            Good('+ pr12'),
        ],
        expected='["+ pr12"]',
    ),
    TCase(
        cmd='m npm add_tags --branch default_branch scope/pkg 0.0.0-pr12.b123',
        eval_cmd_side_effects=[
            Bad(Issue('SOME ERROR')),
        ],
        errors=[
            'dist-tag add issues',
            'SOME ERROR',
        ],
        exit_code=1,
    ),
    TCase(
        cmd='m npm clean_tags scope/pkg',
        eval_cmd_side_effects=[
            Good('{"tag1":"","tag2":"","tag3":"v3"}'),
            Good('- tag1'),
            Bad(Issue('some_error_tag2')),
        ],
        errors=[
            'dist-tag rm issues',
            'some_error_tag2',
            '- tag1',
        ],
        exit_code=1,
    ),
])
def test_m_npm_dist_tags(tcase: TCase, mocker: MockerFixture) -> None:
    eval_cmd = mocker.patch('m.core.subprocess.eval_cmd')
    eval_cmd.side_effect = tcase.eval_cmd_side_effects
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
