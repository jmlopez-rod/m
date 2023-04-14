from textwrap import dedent
from typing import cast

from m.core import Good, Issue, OneOf, io, is_bad, issue, one_of
from m.github.api import GithubPullRequest, create_pr
from m.github.ci import compare_sha_url
from m.github.cli import get_latest_release
from m.github.graphql.queries.branch_prs import PullRequest
from m.github.graphql.queries.branch_prs import fetch as fetch_branch_prs
from m.log import Logger

from m import git

from .config import Config, read_config
from .release_utils import YES_NO, assert_branch, is_yes

logger = Logger('m.ci.review_release')


def release_pr_body(config: Config, gh_ver: str) -> str:
    """Generate the pull request body.

    Args:
        config: The `m` configuration.
        gh_ver: The current version in Github.

    Returns:
        The text to add to the pull request.
    """
    link = compare_sha_url(config.owner, config.repo, gh_ver, 'HEAD')
    instructions = (
        '**DO NOT** use the merge button. Instead run `m end_release`.'
        if config.uses_git_flow()
        else 'either push the merge button or run `m end_release`'
    )
    return dedent(f"""\
        ## Reviewer directions

        Verify `CHANGELOG.md` contains a summary of the unreleased changes.

        {link}

        ## Author directions

        - Wait for reviewers to approve
        - When approved, {instructions}
    """)


def _git_flow_pr_body(config: Config, branch: str, gh_ver: str) -> str:
    link = compare_sha_url(config.owner, config.repo, gh_ver, 'HEAD')
    master = config.get_master_branch()
    develop = config.get_develop_branch()
    return dedent(f"""\
        ## Backport pull request

        This pull request attempts to merge commits created during the release
        process back to the `{develop}` branch. It should only be merged after
        the `{branch}` branch has been merged to `{master}`.

        ## Unreleased changes

        It may be easier to see the changelog in here. Please verify that
        the unreleased changes are properly documented in the `CHANGELOG`.

        {link}

        ## Merging

        This pull request should be merged via `m end_release` when this
        pull request and the "main" one are approved.
    """)


def acknowledge_git_status(status: str) -> OneOf[Issue, None]:
    """Display the current git status and ask developer to confirm.

    Args:
        status: The raw output of `git status`.

    Returns:
        An issue to stop the operation, otherwise None.
    """
    logger.info('The following changes will be committed', {'git': status})
    response = io.prompt_choices(
        'proceed creating the pull request(s)?',
        YES_NO,
        as_list=False,
    )
    if is_yes(response):
        return Good(None)
    return issue('operation cancelled by user')


def inspect_prs(all_prs: list[PullRequest]) -> OneOf[Issue, None]:
    """Inspect the release pull requests.

    There should not be any pull requests when calling `review_release`.
    This is a one time operation.

    Args:
        all_prs: The list of pull requests.

    Returns:
        An issue if prs already exist, None otherwise.
    """
    prs = [pr for pr in all_prs if pr.closed is False]
    if prs:
        return issue('release is already in review', context={
            'prs': {pr.number: pr.url for pr in prs},
        })
    return Good(None)


def create_prs(
    gh_token: str,
    config: Config,
    release_type: str,
    target_ver: str,
    gh_ver: str,
) -> OneOf[Issue, None]:
    """Create release pull request(s).

    Args:
        gh_token: The GITHUB_TOKEN to use to make api calls to Github.
        config: The m configuration.
        release_type: 'hotfix' or 'release'.
        target_ver: The version to release.
        gh_ver: The current version in Github.

    Returns:
        An issue if there is a problem while creating or None if successful.
    """
    all_prs: dict[str, str] = {}
    git_branch = f'{release_type}/{target_ver}'
    develop_branch = config.get_develop_branch()
    if config.uses_git_flow():
        title = f'({release_type} to {develop_branch}) {target_ver}'
        backport_pr = create_pr(
            gh_token,
            config.owner,
            config.repo,
            GithubPullRequest(
                title=title,
                body=_git_flow_pr_body(config, git_branch, gh_ver),
                head=git_branch,
                base=develop_branch,
            ),
        ).map(lambda res: cast(str, res.get('html_url', '')))
        if is_bad(backport_pr):
            logger.warning(
                'unable to create backport pull request',
                backport_pr.value,
            )
        else:
            all_prs[title] = cast(str, backport_pr.value)
    title = f'({release_type}) {target_ver}'
    release_pr = create_pr(
        gh_token,
        config.owner,
        config.repo,
        GithubPullRequest(
            title=title,
            body=release_pr_body(config, gh_ver),
            head=git_branch,
            base=config.get_master_branch(),
        ),
    ).map(lambda res: cast(str, res.get('html_url', '')))
    if is_bad(release_pr):
        logger.warning(
            'unable to create release pull request',
            release_pr.value,
        )
    else:
        all_prs[title] = cast(str, release_pr.value)
    if all_prs:
        logger.info('pull requests created', context=all_prs)
        return Good(None)
    return issue('no prs were created, inspect logs for hints')


def _commit_changes(commit_msg: str) -> OneOf[Issue, str]:
    commit_result = git.commit(commit_msg)
    if is_bad(commit_result):
        if 'working tree clean' in f'{commit_result.value}':
            return Good('')
    return commit_result


def review_release(token: str) -> OneOf[Issue, None]:
    """Create release prs.

    Args:
        token: The GITHUB_TOKEN to use to make api calls to Github.

    Returns:
        None if successful, otherwise an issue.
    """
    return one_of(lambda: [
        None
        for branch in git.get_branch()
        for release_type, target_ver in assert_branch(branch, 'review')
        for config in read_config('m')
        for prs in fetch_branch_prs(token, config.owner, config.repo, branch)
        for _ in inspect_prs(prs)
        for _ in git.stage_all()
        for git_status in git.raw_status()
        for _ in acknowledge_git_status(git_status)
        for _ in _commit_changes(f'({release_type}) {target_ver}')
        for _ in git.push_branch(branch)
        for gh_ver in get_latest_release(token, config.owner, config.repo)
        for _ in create_prs(token, config, release_type, target_ver, gh_ver)
    ])
