from textwrap import dedent

import pytest
from m.docker.shell_command import ShellCommand
from pydantic import BaseModel


class TCase(BaseModel):
    id: str
    cmd: ShellCommand
    expected: str


class DockerArgs(BaseModel):
    tag: list[str] = []
    build_arg: list[str] = []
    force_rm: bool = False


@pytest.mark.parametrize(
    'tcase',
    [
        TCase(
            id='no_args',
            cmd=ShellCommand(prog='prog_name'),
            expected='prog_name',
        ),
        TCase(
            id='positional_args',
            cmd=ShellCommand(prog='prog_name', positional=['arg1', 'arg2']),
            expected="""\
                prog_name \\
                arg1 \\
                arg2""",
        ),
        TCase(
            id='optional_args',
            cmd=ShellCommand(
                prog='prog_name subcommand',
                options={
                    '--opt1': 'value1',
                    '--opt2': 'value2',
                    '--tag': ['tag1', 'tag2'],
                    '--my-opt': '"my value"',
                },
                positional=['arg1'],
            ),
            expected="""\
                prog_name subcommand \\
                --my-opt "my value" \\
                --opt1 value1 \\
                --opt2 value2 \\
                --tag tag1 \\
                --tag tag2 \\
                arg1""",
        ),
        TCase(
            id='pydantic',
            cmd=ShellCommand(
                prog='docker build',
                options=DockerArgs(
                    tag=['t1', 't2'],
                    build_arg=['ARG1=1', 'ARG2=2'],
                    force_rm=True,
                ).model_dump(),
            ),
            expected="""\
                docker build \\
                --build-arg ARG1=1 \\
                --build-arg ARG2=2 \\
                --force-rm \\
                --tag t1 \\
                --tag t2""",
        ),
    ],
    ids=lambda tcase: tcase.id,
)
def test_shell_command(tcase: TCase) -> None:
    assert str(tcase.cmd) == dedent(tcase.expected)
