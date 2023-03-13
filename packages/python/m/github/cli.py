from typing import Any

from ..core import one_of
from ..core.fp import Good, OneOf
from ..core.issue import Issue
from ..core.json import get
from .ci import create_ci_query
from .graphql.api import graphql


def get_pr_info(
    token: str,
    owner: str,
    repo: str,
    pr_number: int,
    file_count: int,
) -> OneOf[Issue, Any]:
    """Retrieve the information of the given Github PR.

    Args:
        token: A Github PAT.
        owner: The owner of the repo.
        repo: The name of the repo.
        pr_number: The pull request number in question.
        file_count: The maximum number of files in the pr to retrieve.

    Returns:
        The pull request information.
    """
    query = create_ci_query(
        pr_number,
        include_commit=False,
        include_release=False,
    )
    variables = {
        'owner': owner,
        'repo': repo,
        'pr': pr_number,
        'fc': file_count,
    }
    return one_of(
        lambda: [
            pr_info
            for res in graphql(token, query, variables)
            for pr_info in get(res, 'repository.pullRequest')
        ],
    )


def get_latest_release(
    token: str,
    owner: str,
    repo: str,
) -> OneOf[Issue, str]:
    """Retrieve the latest release for a repo.

    Args:
        token: A Github PAT.
        owner: The owner of the repo.
        repo: The name of the repo.

    Returns:
        The latest release.
    """
    query = """query ($owner: String!, $repo: String!) {
      repository(owner:$owner, name:$repo) {
         releases(last: 1, orderBy: {field: CREATED_AT, direction: ASC}) {
            nodes {
                name
                tagName
                publishedAt
            }
        }
      }
    }"""
    variables = {'owner': owner, 'repo': repo}
    return one_of(
        lambda: [
            tag_name
            for res in graphql(token, query, variables)
            for releases in get(res, 'repository.releases.nodes')
            for tag_name in _get_latest_release(releases)
        ],
    )


def _get_latest_release(releases: list[dict[str, str]]) -> OneOf:
    if releases:
        return get(releases[0], 'tagName')
    return Good('0.0.0')
