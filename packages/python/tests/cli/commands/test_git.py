import pytest
from m.core import Good
from pytest_mock import MockerFixture
from tests.cli.conftest import TCase, assert_streams, run_cli

from m import git


@pytest.mark.parametrize('tcase', [
    TCase(
        cmd='m git branch',
        eval_cmd_side_effects=[Good('topic/hotdog-branch')],
        expected='topic/hotdog-branch',
    ),
    TCase(
        cmd='m git current_sha',
        eval_cmd_side_effects=[Good('abc123')],
        expected='abc123',
    ),
    TCase(
        cmd='m git first_sha',
        eval_cmd_side_effects=[Good('012_zyx')],
        expected='012_zyx',
    ),
    TCase(
        cmd='m git status',
        eval_cmd_side_effects=[
            Good('some unknown message'),
        ],
        expected='unknown',
    ),
    TCase(
        cmd='m git status',
        eval_cmd_side_effects=[
            Good('Untracked files'),
        ],
        expected='untracked',
    ),
])
def test_m_git_cli(tcase: TCase, mocker: MockerFixture) -> None:
    eval_cmd = mocker.patch('m.core.subprocess.eval_cmd')
    eval_cmd.side_effect = tcase.eval_cmd_side_effects
    std_out, std_err = run_cli(tcase.cmd, tcase.exit_code, mocker)
    assert_streams(std_out, std_err, tcase)


@pytest.mark.parametrize('tcase', [
    TCase(
        runner=git.stash,
        cmd='...',
        eval_cmd_side_effects=[Good('it got stashed')],
        expected='it got stashed',
    ),
    TCase(
        runner=git.stash_pop,
        cmd='...',
        eval_cmd_side_effects=[Good('popped stash')],
        expected='popped stash',
    ),
    TCase(
        runner=lambda: git.checkout_branch('yolo'),
        cmd='...',
        eval_cmd_side_effects=[Good('switched branch')],
        expected='switched branch',
    ),
    TCase(
        runner=lambda: git.get_commits('sha1'),
        cmd='...',
        eval_cmd_side_effects=[Good('commit1\ncommit2\n')],
        expected_value=['commit1', 'commit2'],
    ),
    TCase(
        runner=git.stage_all,
        cmd='...',
        eval_cmd_side_effects=[Good('staged all')],
        expected='staged all',
    ),
    TCase(
        runner=git.raw_status,
        cmd='...',
        eval_cmd_side_effects=[Good('raw status')],
        expected='raw status',
    ),
    TCase(
        runner=lambda: git.push_branch('release/1.2.3'),
        cmd='...',
        eval_cmd_side_effects=[Good('pushed branch')],
        expected='pushed branch',
    ),
    TCase(
        runner=lambda: git.commit('yolo'),
        cmd='...',
        eval_cmd_side_effects=[Good('created commit')],
        expected='created commit',
    ),
])
def test_m_git_fns(tcase: TCase, mocker: MockerFixture) -> None:
    eval_cmd = mocker.patch('m.core.subprocess.eval_cmd')
    eval_cmd.side_effect = tcase.eval_cmd_side_effects
    assert tcase.runner is not None
    res = tcase.runner()
    if tcase.expected_value:
        assert res.value == tcase.expected_value
    else:
        assert res.value == tcase.expected


# testing the special case when there are no releases
def test_m_git_get_commits() -> None:
    res = git.get_commits('0.0.0')
    assert res.value is None
