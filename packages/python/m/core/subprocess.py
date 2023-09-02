import shlex
import subprocess as sub  # noqa: S404
from subprocess import STDOUT, CalledProcessError  # noqa: S404

from . import Issue, issue
from .fp import Good, OneOf


def eval_cmd(cmd: str) -> OneOf[Issue, str]:
    """Evaluate a bash command and return its output.

    Args:
        cmd: The shell command to evaluate.

    Returns:
        The output of the command (or an Issue if the command failed).
    """
    command = shlex.split(cmd)
    try:
        out = sub.check_output(command, stderr=STDOUT, shell=False).decode()  # noqa: S603,E501
    except CalledProcessError as ex:
        out = ex.output.decode()
        return issue(
            'command returned a non zero exit code',
            context={'cmd': cmd, 'output': out},
        )
    return Good(out.strip())


def exec_pnpm(pnpm_args: list[str]) -> OneOf[Issue, None]:
    """Execute pnpm with the given arguments.

    This command will execute the pnpm command in the current working directory.

    Args:
        pnpm_args: The arguments to pass to pnpm.

    Returns:
        None if successful.
    """
    # delegating the rest of the work to pnpm
    exit_code = sub.call(['pnpm', *pnpm_args], shell=False)  # noqa: S603, S607
    if exit_code:
        return issue('non_zero_pnpm_exit_code', context={
            'pnpm_args': pnpm_args,
            'exit_code': exit_code,
        })
    return Good(None)
