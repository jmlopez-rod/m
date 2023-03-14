from m.core import Good, Issue, OneOf, issue, one_of, subprocess


def get_branch() -> OneOf[Issue, str]:
    """Get the current git branch name.

    Returns:
        A `OneOf` containing an `Issue` or a string specifying the branch.
    """
    return subprocess.eval_cmd('git rev-parse --abbrev-ref HEAD')


def stage_all() -> OneOf[Issue, str]:
    """Stage the current changes in the branch.

    Returns:
        A `OneOf` containing an `Issue` or the response from `git add .`.
    """
    return subprocess.eval_cmd('git add .').flat_map_bad(
        lambda err: issue('git add failure', cause=err),
    )


def commit(msg: str) -> OneOf[Issue, str]:
    """Create a commit.

    Args:
        msg: commit description.

    Returns:
        A `OneOf` containing an `Issue` or the response from the git command.
    """
    return subprocess.eval_cmd(f'git commit -m "{msg}"').flat_map_bad(
        lambda err: issue('git commit failure', cause=err),
    )


def push_branch(branch: str) -> OneOf[Issue, str]:
    """Push branch.

    Args:
        branch: name of branch to push.

    Returns:
        A `OneOf` containing an `Issue` or the response from the command.
    """
    return subprocess.eval_cmd(f'git push -u origin "{branch}"').flat_map_bad(
        lambda err: issue('git push failure', cause=err),
    )


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
    return subprocess.eval_cmd('git stash pop')


def checkout_branch(branch: str, create: bool = True) -> OneOf[Issue, str]:
    """Checkout a branch.

    Args:
        branch: name of branch to checkout
        create: create new branch

    Returns:
        A `OneOf` containing an `Issue` of the git response.
    """
    opt = '-b' if create else ''
    return subprocess.eval_cmd(f'git checkout {opt} {branch}').flat_map_bad(
        lambda err: issue('git checkout failure', cause=err),
    )


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


def get_commits(
    first: str,
    latest: str = 'HEAD',
) -> OneOf[Issue, list[str] | None]:
    """Get a list of all the commits between two tags.

    May return `None` in the special case when `first` is `0.0.0`.

    Args:
        first: The first tag.
        latest: The second tag, defaults to HEAD.

    Returns:
        A `OneOf` containing an `Issue` or a list of all the commits.
    """
    if first == '0.0.0':
        return Good(None)
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


def raw_status() -> OneOf[Issue, str]:
    """Obtain the output of "git status".

    Returns:
        A `OneOf` containing an `Issue` or the output of "git status".
    """
    return subprocess.eval_cmd('git status')
