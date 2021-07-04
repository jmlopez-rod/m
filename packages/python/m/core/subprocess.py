from subprocess import Popen, PIPE, STDOUT
from . import issue
from .fp import Good, OneOf
from .issue import Issue


def eval_cmd(cmd: str) -> OneOf[Issue, str]:
    """Evaluate a bash command and return its output in a `Good`."""
    with Popen(
        cmd,
        shell=True,
        universal_newlines=True,
        executable="/bin/bash",
        stdout=PIPE,
        stderr=STDOUT
    ) as process:
        out, _ = process.communicate()
        if process.returncode == 0:
            return Good(out.strip())
    return issue(
        'command returned a non zero exit code',
        data={'cmd': cmd, 'output': out})
