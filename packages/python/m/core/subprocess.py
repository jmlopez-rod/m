from subprocess import Popen, PIPE, STDOUT
from .fp import Good
from .issue import issue


def eval_cmd(cmd):
    """Evaluate a bash command and return its output in a `Good`."""
    params = dict(
        shell=True,
        universal_newlines=True,
        executable="/bin/bash",
        stdout=PIPE,
        stderr=STDOUT)
    with Popen(cmd, **params) as process:
        out, _ = process.communicate()
        if process.returncode == 0:
            return Good(out.strip())
    return issue(
        'command returned a non zero exit code',
        data={'cmd': cmd, 'output': out})
