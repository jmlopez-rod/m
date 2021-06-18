from .core import subprocess


def get_branch():
    """Returns a `OneOf` object containing the branch name."""
    return subprocess.eval_cmd('git rev-parse --abbrev-ref HEAD')


def get_first_commit_sha():
    """Returns a `OneOf` object containing the first commit."""
    return subprocess.eval_cmd('git rev-list --max-parents=0 HEAD')


def get_current_commit_sha():
    """Returns a `OneOf` object containing the current commit."""
    return subprocess.eval_cmd('git rev-parse HEAD')
