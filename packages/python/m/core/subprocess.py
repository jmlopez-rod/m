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
