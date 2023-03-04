import sys
from inspect import cleandoc
from io import StringIO
from typing import Any, Callable, Tuple

import pytest
from m.__main__ import main
from pydantic import BaseModel
from pytest_mock import MockerFixture


class TCase(BaseModel):
    """Basic test case for cli commands."""

    runner: Callable[[], Any] | None = None
    cmd: str | list[str]
    expected_value: Any = None
    expected: str = ''
    errors: list[str] = []
    banned_errors: list[str] = []
    eval_cmd_side_effects: list[Any] = []
    exit_code: int = 0
    cleandoc: bool = True
    new_line: bool = True
    std_in: str | None = None


def run_cli(
    cmd: str | list[str],
    exit_code: int,
    mocker: MockerFixture,
) -> Tuple[str, str]:
    std_out = StringIO()
    std_err = StringIO()
    argv = cmd if isinstance(cmd, list) else cmd.split(' ')
    mocker.patch.object(sys, 'argv', argv)
    mocker.patch.object(sys, 'stdout', std_out)
    mocker.patch.object(sys, 'stderr', std_err)

    prog = None
    with pytest.raises(SystemExit) as prog_block:
        prog = prog_block
        main()
    # Would be nice to be able to reset via a the mocker
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    assert prog is not None

    if prog.value.code != exit_code:
        # display the captured stderr to debug
        print(std_out.getvalue(), file=sys.stdout)
        print(std_err.getvalue(), file=sys.stderr)
    assert prog.value.code == exit_code

    return std_out.getvalue(), std_err.getvalue()


def assert_streams(
    out: str,
    err: str,
    tcase: TCase,
) -> None:
    if tcase.errors:
        for error in tcase.errors:
            assert error in err
    if tcase.banned_errors:
        for banned_error in tcase.banned_errors:
            assert banned_error not in err
    expected = (
        cleandoc(tcase.expected)
        if tcase.cleandoc
        else tcase.expected
    )
    expected_str = f'{expected}\n' if tcase.new_line else expected
    if expected and out != '\n':
        assert out == expected_str


def cli_params(params: dict[str, str]) -> list[str]:
    return [
        param_item
        for param_name, param_val in params.items()
        for param_item in (param_name, param_val)
    ]
