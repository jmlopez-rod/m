import pytest
from m.core import Good
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase, assert_streams, run_cli


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd='m git branch',
        eval_cmd_side_effects=[Good('topic/hotdog-branch')],
        expected='topic/hotdog-branch'
    ),
    TCase(
        cmd='m git current_sha',
        eval_cmd_side_effects=[Good('abc123')],
        expected='abc123'
    ),
    TCase(
        cmd='m git first_sha',
        eval_cmd_side_effects=[Good('012_zyx')],
        expected='012_zyx'
    ),
    TCase(
        cmd='m git status',
        eval_cmd_side_effects=[
            Good("some unknown message"),
        ],
        expected='?'
    ),
    TCase(
        cmd='m git status',
        eval_cmd_side_effects=[
            Good("Untracked files"),
        ],
        expected='untracked'
    ),

])
def test_m_git_branch(tcase: TCase, mocker: MockerFixture) -> None:
    eval_cmd = mocker.patch('m.core.subprocess.eval_cmd')
    eval_cmd.side_effect = tcase.eval_cmd_side_effects
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)
