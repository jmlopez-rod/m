from subprocess import PIPE, STDOUT, Popen

from . import Issue, issue
from .fp import Good, OneOf


def eval_cmd(cmd: str) -> OneOf[Issue, str]:
    """Evaluate a bash command and return its output.

    Args:
        cmd: The shell command to evaluate.

    Returns:
        The output of the command (or an Issue if the command failed).
    """
    with Popen(
        cmd,
        shell=True,
        universal_newlines=True,
        executable='/bin/bash',
        stdout=PIPE,
        stderr=STDOUT,
    ) as process:
        out, _ = process.communicate()
        if process.returncode == 0:
            return Good(out.strip())
    return issue(
        'command returned a non zero exit code',
        context={'cmd': cmd, 'output': out},
    )
