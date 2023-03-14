import sys
import time
from functools import partial
from typing import Callable

from m.core import Good, Issue, OneOf, issue, one_of
from m.github.api import merge_pr
from m.github.cli import get_latest_release
from m.github.graphql.enums import MergeableState
from m.github.graphql.queries.branch_prs import PullRequest
from m.github.graphql.queries.branch_prs import fetch as fetch_branch_prs
from m.log import Logger

from m import git

from .config import Config, read_config
from .release_utils import assert_branch

logger = Logger('m.ci.start_release')
_checks_per_line = 30


def inspect_prs(prs: list[PullRequest]) -> OneOf[Issue, None]:
    """Inspect the release pull requests.

    Attempts to warn the users of possible issues that may be encountered.

    Args:
        prs: The list of pull requests to merge.

    Returns:
        An issue if the user decides to cancel, None otherwise.
    """
    if not prs:
        return issue('no prs associated with the release/hotfix branch')
    conflicting = [
        pr
        for pr in prs
        if pr.mergeable == MergeableState.conflicting
    ]
    if conflicting:
        return issue('found conflicting prs', context={
            'prs': {pr.number: pr.url for pr in conflicting},
            'suggestion': 'check out the pull requests',
        })
    # Nice to have: handle code reviews - warn if there are requested changes
    # To introduce this we need to prompt the user if we should proceed to
    # merge the pr even when there are pending reviews. This is mainly
    # done for admins that may be able to merge without approvals.
    return Good(None)


def wait_until(
    predicate: Callable[[], OneOf[Issue, bool]],
) -> OneOf[Issue, None]:
    """Sleep until the predicate function returns False.

    Will print a `.` (dot) every 10 seconds thus every 6 dots
    denote a minute.

    Args:
        predicate: function returning an Issue or a boolean

    Returns:
        An issue or None.
    """
    should_loop = predicate()
    counter = 0
    indent = '       '
    sys.stdout.write(indent)
    while not should_loop.is_bad and should_loop.value is True:
        time.sleep(10)
        counter += 1
        modifier = ''
        if counter % 6 == 0:
            modifier = '    '
        if counter % _checks_per_line == 0:
            modifier = f'\n{indent}'
        sys.stdout.write(f'.{modifier}')
        sys.stdout.flush()
        should_loop = predicate()
    sys.stdout.write('\n')
    return should_loop.map(lambda _: None)


def merge_prs(
    gh_token: str,
    config: Config,
    prs: list[PullRequest],
    target_ver: str,
) -> OneOf[Issue, None]:
    """Merge the given prs.

    Args:
        gh_token: The GITHUB_TOKEN to use to make api calls to Github.
        config: The m configuration.
        prs: The pull requests to merge.
        target_ver: The version to release.

    Returns:
        An issue if there is a problem while merging or None if successful.
    """
    master_branch = config.get_master_branch()
    first_index = 0 if prs[0].base_ref_name == master_branch else 1
    second_index = 0 if first_index == 1 else 1
    first_pr = prs[first_index]
    second_pr = None
    if len(prs) == 2:
        second_pr = prs[second_index]

    first_merged_result: OneOf[Issue, None]
    if first_pr.merged or first_pr.closed:
        msg = f'{master_branch} branch pr already merged/closed'
        logger.warning(msg, context={
            'pr_info': first_pr.dict(),
        })
        first_merged_result = Good(None)
    else:
        msg = f'merged pr{first_pr.number} to {master_branch}'
        first_merged_result = merge_pr(
            gh_token,
            config.owner,
            config.repo,
            first_pr.number,
            None,
        ).map(lambda res: logger.info(msg, res)).map(lambda _: None)

    return one_of(lambda: [
        None
        for _ in first_merged_result
        for _ in _merge_second_pr(gh_token, config, second_pr, target_ver)
    ])


def _not_released(
    token: str,
    owner: str,
    repo: str,
    ver: str,
) -> OneOf[Issue, bool]:
    latest = get_latest_release(token, owner, repo)
    return latest.map(lambda current_ver: current_ver != ver)


def _merge_second_pr(
    gh_token: str,
    config: Config,
    pr: PullRequest | None,
    target_ver: str,
) -> OneOf[Issue, None]:
    if not pr:
        return Good(None)
    base_ref = pr.base_ref_name
    if pr.merged or pr.closed:
        logger.warning(f'{base_ref} branch pr already merged/closed', context={
            'pr_info': pr.dict(),
        })
        return Good(None)
    ver = target_ver
    owner = config.owner
    repo = config.repo
    pr_num = pr.number
    not_released = partial(_not_released, gh_token, owner, repo, ver)
    logger.info(f'checking every 10 seconds until {ver} is released')
    return one_of(lambda: [
        None
        for _ in wait_until(not_released)
        for res in merge_pr(gh_token, owner, repo, pr_num, None)
        for _ in logger.info(f'merged pr{pr_num} to {base_ref}', res)
    ])


def _switch_branch(branch: str, checkout: str) -> OneOf[Issue, None]:
    return logger.info(f'release complete - switching to "{branch}" branch', {
        'git': f'{checkout}\n',
    }).map(lambda _: None)


def end_release(gh_token: str) -> OneOf[Issue, None]:
    """End the release process.

    Args:
        gh_token: The GITHUB_TOKEN to use to make api calls to Github.

    Returns:
        None if successful, otherwise an issue.
    """
    return one_of(lambda: [
        None
        for branch in git.get_branch()
        for _, target_ver in assert_branch(branch, 'end')
        for config in read_config('m')
        for prs in fetch_branch_prs(
            gh_token,
            config.owner,
            config.repo,
            branch,
        )
        for _ in inspect_prs(prs)
        for _ in merge_prs(gh_token, config, prs, target_ver)
        for default_branch in Good[Issue, str](config.get_default_branch())
        for checkout in git.checkout_branch(default_branch, create=False)
        for _ in _switch_branch(default_branch, checkout)
    ])
