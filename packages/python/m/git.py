from .core import one_of, subprocess
from .core.fp import OneOf
from .core.issue import Issue


def get_branch() -> OneOf[Issue, str]:
    """Return a `OneOf` object containing the branch name."""
    return subprocess.eval_cmd('git rev-parse --abbrev-ref HEAD')


def get_first_commit_sha() -> OneOf[Issue, str]:
    """Return a `OneOf` object containing the first commit."""
    return subprocess.eval_cmd('git rev-list --max-parents=0 HEAD')


def get_current_commit_sha() -> OneOf[Issue, str]:
    """Returns a `OneOf` object containing the current commit."""
    return subprocess.eval_cmd('git rev-parse HEAD')


def get_remote_url() -> OneOf[Issue, str]:
    """Returns a `OneOf` object containing the remote url."""
    return subprocess.eval_cmd('git config --get remote.origin.url')


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


def get_status() -> OneOf[Issue, str]:
    """Return a `OneOf` containing the current git status."""
    res = subprocess.eval_cmd('git status')
    return one_of(lambda: [
        _extract_status(msg)
        for msg in res
    ])
