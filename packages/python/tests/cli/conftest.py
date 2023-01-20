import sys
from inspect import cleandoc
from io import StringIO
from typing import Any, Tuple

import pytest
from m.__main__ import main
from pydantic import BaseModel
from pytest_mock import MockerFixture


class TCase(BaseModel):
    """Basic test case for cli commands."""

    cmd: str | list[str]
    expected: str = ''
    errors: list[str] = []
    eval_cmd_side_effects: list[Any] = []
    exit_code: int = 0
    cleandoc: bool = True


def run_cli(
    cmd: str | list[str],
    exit_code: int,
    mocker: MockerFixture,
) -> Tuple[StringIO, StringIO]:
    std_out = StringIO()
    std_err = StringIO()
    argv = cmd if isinstance(cmd, list) else cmd.split(' ')
    og_std_err = sys.stderr

    mocker.patch.object(sys, 'argv', argv)
    mocker.patch.object(sys, 'stdout', std_out)
    mocker.patch.object(sys, 'stderr', std_err)

    prog = None
    with pytest.raises(SystemExit) as prog_block:
        prog = prog_block
        main()
    assert prog is not None
    if prog.value.code != exit_code:
        print(std_err.getvalue(), file=og_std_err)
    assert prog.value.code == exit_code

    return std_out, std_err


def assert_streams(
    out: StringIO,
    err: StringIO,
    tcase: TCase,
) -> None:
    if tcase.errors:
        err_str = err.getvalue()
        for error in tcase.errors:
            assert error in err_str
    else:
        expected = (
            cleandoc(tcase.expected)
            if tcase.cleandoc
            else tcase.expected
        )
        assert out.getvalue() == f'{expected}\n'
