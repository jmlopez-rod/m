from textwrap import dedent
from typing import Any, cast

from m.core import Good, Issue, OneOf, io, is_bad, issue, one_of
from m.github.api import GithubPullRequest, create_pr
from m.github.ci import compare_sha_url
from m.github.graphql.queries.branch_prs import PullRequest
from m.github.graphql.queries.branch_prs import fetch as fetch_branch_prs
from m.log import Logger

from m import git

from .config import Config, read_config

logger = Logger('m.ci.review_release')
YES_NO = ('yes', 'no')


def release_pr_body(config: Config) -> str:
    """Generate the pull request body.

    Args:
        config: The `m` configuration.

    Returns:
        The text to add to the pull request.
    """
    link = compare_sha_url(config.owner, config.repo, config.version, 'HEAD')
    instructions = (
        '**DO NOT** use the merge button. Instead run `m end_release`.'
        if config.uses_git_flow()
        else 'either push the merge button or run `m end_release`'
    )
    return dedent(f"""\
        ## Reviewer directions

        Verify `CHANGELOG.md` contains a summary describing the unreleased
        changes.

        {link}

        ## Pull Request author directions

        - Wait for reviewers to approve
        - When approved, {instructions}
    """)


def _git_flow_pr_body(config: Config, branch: str) -> str:
    link = compare_sha_url(config.owner, config.repo, config.version, 'HEAD')
    return dedent(f"""\
        ## Backport pull request

        This pull request attempts to merge commits created during the release
        process back to the `develop` branch. It should only be merged after
        the `{branch}` branch has been merged.

        ## Unreleased changes

        It may be easier to see the changelog in here. Please verify that
        the unreleased changes are properly documented in the CHANGELOG.

        {link}

        ## Merging

        If possible this pr should be merged via `m end_release` when this
        pull request and the "main" one are approved.
    """)


def _is_yes(user_response: str) -> bool:
    return user_response == 'yes'


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
    if _is_yes(response):
        return Good(None)
    return issue('operation cancelled by user')


def assert_branch(branch: str) -> OneOf[Issue, tuple[str, str]]:
    """Assert that the end of a release is done in the proper branch.

    This can only happen in `release/x.y.z` or `hotfix/x.y.z`.

    Args:
        branch: branch name to verify.

    Returns:
        An Issue if the current branch is not a release/hotfix else the
        version to release/hotfix.
    """
    valid_prefix = ('release/', 'hotfix/')
    if branch.startswith(valid_prefix):
        parts = branch.split('/')
        return Good((parts[0], parts[1]))
    return issue(
        'review_release can only be done from a release/hotfix branch',
        context={
            'current_branch': branch,
            'expected': 'release/x.y.z or hotfix/x.y.z',
        },
    )


def inspect_prs(prs: list[PullRequest]) -> OneOf[Issue, None]:
    """Inspect the release pull requests.

    There should not be any pull requests when calling `review_release`.
    This is a one time operation.

    Args:
        prs: The list of pull requests.

    Returns:
        An issue if prs already exist, None otherwise.
    """
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
) -> OneOf[Issue, None]:
    """Create release pull request(s).

    Args:
        gh_token: The GITHUB_TOKEN to use to make api calls to Github.
        config: The m configuration.
        release_type: 'hotfix' or 'release'.
        target_ver: The version to release.

    Returns:
        An issue if there is a problem while creating or None if successful.
    """
    second_pr: OneOf[Issue, Any] = Good(None)
    all_prs: dict[str, str] = {}
    git_branch = f'{release_type}/{target_ver}'
    if config.uses_git_flow():
        title = f'({release_type} to develop) {target_ver}'
        backport_pr = create_pr(
            gh_token,
            config.owner,
            config.repo,
            GithubPullRequest(
                title=title,
                body=_git_flow_pr_body(config, git_branch),
                head=git_branch,
                base=config.get_develop_branch(),
            ),
        ).map(lambda res: cast(str, res.get('html_url', '')))
        if is_bad(backport_pr):
            logger.warning(
                'unable to create backport pull request',
                backport_pr.value,
            )
        else:
            all_prs[title] = cast(str, second_pr.value)
    title = f'({release_type}) {target_ver}'
    release_pr = create_pr(
        gh_token,
        config.owner,
        config.repo,
        GithubPullRequest(
            title=title,
            body=release_pr_body(config),
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
        for release_type, target_ver in assert_branch(branch)
        for config in read_config('m')
        for prs in fetch_branch_prs(token, config.owner, config.repo, branch)
        for _ in inspect_prs(prs)
        for _ in git.stage_all()
        for git_status in git.raw_status()
        for _ in acknowledge_git_status(git_status)
        for _ in git.commit(f'({release_type}) {target_ver}')
        for _ in git.push_branch(branch)
        for _ in create_prs(token, config, release_type, target_ver)
    ])
