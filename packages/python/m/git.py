from m.core import Bad, Good, Res, hone, one_of, subprocess


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


def pull() -> Res[str]:
    """Pull branch.

    Returns:
        A `OneOf` containing an `Issue` or the response from the git command.
    """
    res = subprocess.eval_cmd('git pull')
    return res.flat_map_bad(hone('git pull failure'))


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


def _list_tags(tag_response: str) -> dict[str, str]:
    lines = tag_response.strip().splitlines()
    split_lines = (line.split('\trefs/tags/') for line in lines)
    return {tag: sha for sha, tag in split_lines}


def list_tags(pattern: str) -> Res[dict[str, str]]:
    """List all the tags matching a pattern.

    Args:
        pattern: The pattern to match.

    Returns:
        A `OneOf` containing an `Issue` or a string specifying the branch.
    """
    cmd = f'git ls-remote --tags origin -l "{pattern}"'
    return one_of(
        lambda: [
            _list_tags(output)
            for output in subprocess.eval_cmd(cmd)
        ],
    )


def remove_git_tag(tag: str) -> Res[str]:
    """Remove a git tag.

    It is important to remove the local tag before removing the remote tag.

    Args:
        tag: The tag to remove.

    Returns:
        A `OneOf` containing an `Issue` or the response from the git command.
    """
    tag_ref = f'refs/tags/{tag}'
    return one_of(lambda: [
        f'{local}\n{remote}'
        for _ in subprocess.eval_cmd(f'git fetch origin +{tag_ref}:{tag_ref}')
        for local in subprocess.eval_cmd(f'git tag -d {tag}')
        for remote in subprocess.eval_cmd(f'git push origin :{tag_ref}')
    ])


def update_git_tag(
    tag: str,
    sha: str,
    remote_tags: list[str],
    *,
    skip: bool = False,
) -> Res[str]:
    """Create or move a git tag.

    The remote_tags should be provided to determine if we need to remove them
    before moving the tag. See https://stackoverflow.com/a/28280404 for more
    details on the git commands.

    Args:
        tag: The tag to set.
        sha: The commit sha to set the tag to.
        remote_tags: The list of remote tags.
        skip: Skip process if set to true.

    Returns:
        A `OneOf` containing an `Issue` or the response from the git command.
    """
    if skip:
        return Good(f'skipping {tag}')
    removal_output = ''
    if tag in remote_tags:
        removal_res = remove_git_tag(tag)
        if isinstance(removal_res, Bad):
            return Bad(removal_res.value)
        removal_output = f'{removal_res.value}\n'
    return one_of(lambda: [
        f'{removal_output}{local}\n{remote}'
        for local in subprocess.eval_cmd(f'git tag {tag} {sha}')
        for remote in subprocess.eval_cmd(f'git push origin {tag}')
    ])


def tag_release(version: str, sha: str, *, major_only: bool) -> Res[str]:
    """Create a git tags for a release.

    This is done to keep a major and minor versions tags pointing to the latest.

    Args:
        version: The version to tag.
        sha: The commit sha to tag.
        major_only: Only create the major tag.

    Returns:
        A `OneOf` containing an `Issue` or the response from the git command.
    """
    v_parts = version.split('.')
    # Assuming the version is valid
    major, minor = v_parts[0], v_parts[1]
    major_tag = f'v{major}'
    minor_tag = f'v{major}.{minor}'

    return one_of(lambda: [
        '\n'.join([major_out, minor_out])
        for all_tags in list_tags(f'v{major}*')
        for major_out in update_git_tag(major_tag, sha, list(all_tags))
        for minor_out in update_git_tag(
            minor_tag,
            sha,
            list(all_tags),
            skip=major_only,
        )
    ])
