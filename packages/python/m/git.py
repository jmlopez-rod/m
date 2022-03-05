from .core import one_of, subprocess
from .core.fp import OneOf
from .core.issue import Issue


def get_branch() -> OneOf[Issue, str]:
    """Get the current git branch name.

    Returns:
        A `OneOf` containing an `Issue` or a string specifying the branch.
    """
    return subprocess.eval_cmd('git rev-parse --abbrev-ref HEAD')


def get_first_commit_sha() -> OneOf[Issue, str]:
    """Find the first commit sha in the repository.

    Returns:
        A `OneOf` containing an `Issue` or a string of the first commit sha.
    """
    return subprocess.eval_cmd('git rev-list --max-parents=0 HEAD')


def get_current_commit_sha() -> OneOf[Issue, str]:
    """Find the sha of the current commit.

    Returns:
        A `OneOf` containing an `Issue` or a string of the current commit sha.
    """
    return subprocess.eval_cmd('git rev-parse HEAD')


def get_remote_url() -> OneOf[Issue, str]:
    """Find the remote url of the repo.

    Returns:
        A `OneOf` containing an `Issue` or a string with the url.
    """
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
    """Find the current git status.

    Returns:
        A `OneOf` containing an `Issue` or a word denoting the git status.
    """
    res = subprocess.eval_cmd('git status')
    return one_of(
        lambda: [
            _extract_status(msg)
            for msg in res
        ],
    )
