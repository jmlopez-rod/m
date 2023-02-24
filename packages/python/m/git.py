from m.core import one_of, subprocess
from m.core.fp import OneOf
from m.core.issue import Issue


def get_branch() -> OneOf[Issue, str]:
    """Get the current git branch name.

    Returns:
        A `OneOf` containing an `Issue` or a string specifying the branch.
    """
    return subprocess.eval_cmd('git rev-parse --abbrev-ref HEAD')


def stash() -> OneOf[Issue, str]:
    """Stash the current changes in the branch.

    Returns:
        A `OneOf` containing an `Issue` or the response from `git stash`.
    """
    return subprocess.eval_cmd('git stash')


def stash_pop() -> OneOf[Issue, str]:
    """Pop the changes stored in the git stash.

    Returns:
        A `OneOf` containing an `Issue` or the response from `git stash pop`.
    """
    return subprocess.eval_cmd('git stash')


def checkout_branch(branch: str) -> OneOf[Issue, str]:
    """Checkout a branch.

    Args:
        branch: name of branch to checkout

    Returns:
        A `OneOf` containing an `Issue` of the git response.
    """
    return subprocess.eval_cmd(f'git checkout -b {branch}')


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


def get_commits(first: str, latest: str = 'HEAD') -> OneOf[Issue, list[str]]:
    """Get a list of all the commits between two tags.

    Args:
        first: The first tag.
        latest: The second tag, defaults to HEAD.

    Returns:
        A `OneOf` containing an `Issue` or a list of all the commits.
    """
    cmd = f'git log {latest}...{first} --oneline --no-color'
    return subprocess.eval_cmd(cmd).map(lambda out: out.splitlines())


def _extract_status(msg: str) -> tuple[str, str]:
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
            return key, substr
    return '?', 'unknown'


def get_status() -> OneOf[Issue, tuple[str, str]]:
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
