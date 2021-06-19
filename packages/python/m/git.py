from .core import subprocess
from .core.fp import one_of


def get_branch():
    """Returns a `OneOf` object containing the branch name."""
    return subprocess.eval_cmd('git rev-parse --abbrev-ref HEAD')


def get_first_commit_sha():
    """Returns a `OneOf` object containing the first commit."""
    return subprocess.eval_cmd('git rev-list --max-parents=0 HEAD')


def get_current_commit_sha():
    """Returns a `OneOf` object containing the current commit."""
    return subprocess.eval_cmd('git rev-parse HEAD')


def _extract_status(msg: str) -> str:
    matches = [
        ('Untracked files', 'untracked'),
        ('Your branch is ahead', 'ahead'),
        ('Your branch is behind', 'behind'),
        ('working tree clean', 'clean'),
        ('Changes to be committed', 'staged'),
        ('Changed but not updated', 'dirty'),
        ('Changes not staged', 'dirty'),
        ('Unmerged paths', 'dirty'),
        ('diverged', 'diverged'),
    ]
    for substr, key in matches:
        if substr in msg:
            return key
    return '?'


def get_status():
    """Return a `OneOf` containing the current git status."""
    res = subprocess.eval_cmd('git status')
    return one_of(lambda: [
        _extract_status(msg)
        for msg in res
    ])
