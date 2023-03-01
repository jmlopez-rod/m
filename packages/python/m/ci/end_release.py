from m.core import Good, Issue, OneOf, issue, one_of
from m.github.graphql.enums import MergeableState
from m.github.graphql.queries.branch_prs import PullRequest
from m.github.graphql.queries.branch_prs import fetch as fetch_branch_prs
from m.log import Logger

from m import git

from .config import read_config

logger = Logger('m.ci.start_release')


def assert_branch(branch: str) -> OneOf[Issue, None]:
    """Assert that the end of a release is done in the proper branch.

    This can only happen in `release/x.y.z` or `hotfix/x.y.z`.

    Args:
        branch: branch name to verify.

    Returns:
        An Issue if the current branch is not a release/hotfix.
    """
    valid_prefix = ('release/', 'hotfix/')
    if branch.startswith(valid_prefix):
        return Good(None)
    return issue(
        'end_release can only be done from a release/hotfix branch',
        context={
            'current_branch': branch,
            'expected': 'release/x.y.z or hotfix/x.y.z',
        },
    )


def inspect_prs(prs: list[PullRequest]) -> OneOf[Issue, None]:
    """Inspect the release pull requests.

    Attempts to warn the users of possible issues that may be encountered.

    Args:
        prs: The list of pull requests to merge.

    Returns:
        An issue if the user decides to cancel, None otherwise.
    """
    conflicting = [
        pr
        for pr in prs
        if pr.mergeable == MergeableState.conflicting
    ]
    if conflicting:
        return issue('found conflicting prs', context={
            'prs': {pr.number: pr.url for pr in conflicting},
        })
    return Good(None)


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
        for _ in assert_branch(branch)
        for config in read_config('m')
        for prs in fetch_branch_prs(
            gh_token,
            config.owner,
            config.repo,
            branch,
        )
        for _ in inspect_prs(prs)
    ])
