from m.core import Good, Issue, OneOf, io, is_bad, issue, one_of
from m.github.cli import get_latest_release
from m.log import Logger

from m import git

from .assert_branch import assert_branch
from .release_setup import release_setup
from .release_utils import YES_NO, is_yes

logger = Logger('m.ci.start_release')


def assert_git_status(status: str, description: str) -> OneOf[Issue, bool]:
    """Assert that the current branch is in a clean state.

    This action may stash some changes. This happens when the developer works
    on a hotfix and starts making changes directly in the branch.

    Args:
        status: short key describing the status
        description: The text used to determine the status

    Returns:
        An issue explaining why we cannot complete the release setup. If
        successful it will return a boolean value. A true value means that
        the process stashed changes and they will need to be popped.
    """
    if status == 'clean':
        logger.info('branch is in a clean state')
        return Good(False)
    if status in {'ahead', 'behind'}:
        return issue(
            'branch is not in sync with the remote branch',
            context={
                'git_status': description,
                'suggestion': 'try running `git pull` and/or `git push`',
            },
        )
    can_stash = {
        'Untracked files',
        'Changes to be committed',
        'Changed but not updated',
        'Changes not staged',
    }
    if description in can_stash:
        logger.warning(f'git status: {description}')
        response = io.prompt_choices(
            'would you like to stash the changes and continue?',
            YES_NO,
            as_list=False,
        )
        if is_yes(response):
            return one_of(lambda: [
                True
                for cmd_out in git.stash()
                for _ in logger.info('ran `git stash`', {'git': cmd_out})
            ]).flat_map_bad(lambda err: issue('git stash failure', cause=err))
    return issue(
        'releases can only be done in a clean git state',
        context={
            'git_status': status,
            'description': description,
        },
    )


def verify_release(
    commits: list[str] | None,
    hotfix: bool,
) -> OneOf[Issue, None]:
    """Compare the number of commits to verify if the release should proceed.

    In some cases we may start a hotfix without realizing that there are
    already some commits in the branch that have not been released. In this
    case it should have been a full release instead.

    This step can be skipped if `commits` is `None`.

    Args:
        commits: List of unreleased commits.
        hotfix: flag to let us know if the release is a hotfix.

    Returns:
        None if everything is good, otherwise an issue.
    """
    if commits is None:
        return Good(None)
    if hotfix and len(commits):
        logger.warning('hotfix may contain unreleased features', {
            'commits': commits,
        })
        response = io.prompt_choices(
            'Disregard warning and proceed with hotfix?',
            YES_NO,
            as_list=False,
        )
        if is_yes(response):
            return Good(None)
        return issue('hotfix aborted by user', context={
            'commits': commits,
            'suggestion': 'consider creating a release',
        })
    if not commits and not hotfix:
        logger.warning('there are no commits to release')
        response = io.prompt_choices(
            'Proceed with a release instead of a hotfix?',
            YES_NO,
            as_list=False,
        )
        if is_yes(response):
            return Good(None)
        return issue('release aborted by user', context={
            'commits': 'no commits to release',
            'suggestion': 'consider creating a hotfix',
        })
    return Good(None)


def after_checkout(branch_checkout: str, stashed: bool) -> OneOf[Issue, None]:
    """Notify the user that the branch has switched.

    Optionally if there are stashed changes they will be popped.

    Args:
        branch_checkout: output from git checkout.
        stashed: If True, it will run git stash pop.

    Returns:
        A OneOf with None. There should be no issues. A warning may show up.
    """
    logger.info('branch checkout successful', {
        'git': f'{branch_checkout}\n',
    })
    if stashed:
        pop_result = git.stash_pop()
        if is_bad(pop_result):
            logger.warning('`git stash pop` issue', pop_result.value)
        else:
            logger.info('stashed files have been restored')
    return Good(None)


def _get_commits(gh_ver: str) -> OneOf[Issue, list[str] | None]:
    either = git.get_commits(gh_ver)
    if is_bad(either):
        logger.warning(
            'unable to retrieve unreleased commits - skipping checks',
            either.value,
        )
        return Good(None)
    return either


def start_release(gh_token: str, hotfix: bool = False) -> OneOf[Issue, None]:
    """Start the release process.

    Args:
        gh_token: The GITHUB_TOKEN to use to make api calls to Github.
        hotfix: Set to true to start a hotfix.

    Returns:
        None if successful, otherwise an issue.
    """
    release_type = 'hotfix' if hotfix else 'release'
    return one_of(lambda: [
        None
        for config in assert_branch(release_type, 'm')
        for status, description in git.get_status()
        for stashed_changes in assert_git_status(status, description)
        for gh_ver in get_latest_release(gh_token, config.owner, config.repo)
        for commits in _get_commits(gh_ver)
        for _ in verify_release(commits, hotfix=hotfix)
        for new_ver in io.prompt_next_version(gh_ver, release_type)
        for branch_checkout in git.checkout_branch(f'{release_type}/{new_ver}')
        for _ in after_checkout(branch_checkout, stashed_changes)
        for _ in release_setup('m', config, new_ver)
    ])
