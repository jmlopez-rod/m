from m.core import Good, Res, hone, one_of, subprocess


def get_branch() -> Res[str]:
    """Get the current git branch name.

    Returns:
        A `OneOf` containing an `Issue` or a string specifying the branch.
    """
    return subprocess.eval_cmd('git rev-parse --abbrev-ref HEAD')


def stage_all() -> Res[str]:
    """Stage the current changes in the branch.

    Returns:
        A `OneOf` containing an `Issue` or the response from `git add .`.
    """
    res = subprocess.eval_cmd('git add .')
    return res.flat_map_bad(hone('git add failure'))


def commit(msg: str) -> Res[str]:
    """Create a commit.

    Args:
        msg: commit description.

    Returns:
        A `OneOf` containing an `Issue` or the response from the git command.
    """
    res = subprocess.eval_cmd(f'git commit -m "{msg}"')
    return res.flat_map_bad(hone('git commit failure'))


def push_branch(branch: str) -> Res[str]:
    """Push branch.

    Args:
        branch: name of branch to push.

    Returns:
        A `OneOf` containing an `Issue` or the response from the command.
    """
    res = subprocess.eval_cmd(f'git push -u origin "{branch}"')
    return res.flat_map_bad(hone('git push failure'))


def stash() -> Res[str]:
    """Stash the current changes in the branch.

    Returns:
        A `OneOf` containing an `Issue` or the response from `git stash`.
    """
    return subprocess.eval_cmd('git stash')


def stash_pop() -> Res[str]:
    """Pop the changes stored in the git stash.

    Returns:
        A `OneOf` containing an `Issue` or the response from `git stash pop`.
    """
    return subprocess.eval_cmd('git stash pop')


def checkout_branch(branch: str, create: bool = True) -> Res[str]:
    """Checkout a branch.

    Args:
        branch: name of branch to checkout
        create: create new branch

    Returns:
        A `OneOf` containing an `Issue` of the git response.
    """
    opt = '-b' if create else ''
    res = subprocess.eval_cmd(f'git checkout {opt} {branch}')
    return res.flat_map_bad(hone('git checkout failure'))


def get_first_commit_sha() -> Res[str]:
    """Find the first commit sha in the repository.

    Returns:
        A `OneOf` containing an `Issue` or a string of the first commit sha.
    """
    return subprocess.eval_cmd('git rev-list --max-parents=0 HEAD')


def get_current_commit_sha() -> Res[str]:
    """Find the sha of the current commit.

    Returns:
        A `OneOf` containing an `Issue` or a string of the current commit sha.
    """
    return subprocess.eval_cmd('git rev-parse HEAD')


def get_repo_path() -> Res[str]:
    """Get the absolute path to the repository.

    Returns:
        An issue or a string of the path to the repo.
    """
    return subprocess.eval_cmd('git rev-parse --show-toplevel')


def get_remote_url() -> Res[str]:
    """Find the remote url of the repo.

    Returns:
        A `OneOf` containing an `Issue` or a string with the url.
    """
    return subprocess.eval_cmd('git config --get remote.origin.url')


def get_commits(
    first: str,
    latest: str = 'HEAD',
) -> Res[list[str] | None]:
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
    return 'unknown', 'unknown'


def get_status(*, check_stash: bool = False) -> Res[tuple[str, str]]:
    """Find the current git status.

    Note that checking for stashed changes is not part of the regular git
    status. To opt in you must set `check_stash=True`.

    Args:
        check_stash: Check if there are any stashed changes.

    Returns:
        A `OneOf` containing an `Issue` or a word denoting the git status.
    """
    res = subprocess.eval_cmd('git status')
    if check_stash:
        stash_files = subprocess.eval_cmd('git stash show').get_or_else('')
        has_untracked = res.get_or_else('').startswith('Untracked files')
        if not has_untracked and stash_files:
            return Good(('stash', 'stash'))
    return one_of(
        lambda: [
            _extract_status(msg)
            for msg in res
        ],
    )


def raw_status() -> Res[str]:
    """Obtain the output of "git status".

    Returns:
        A `OneOf` containing an `Issue` or the output of "git status".
    """
    return subprocess.eval_cmd('git status')
