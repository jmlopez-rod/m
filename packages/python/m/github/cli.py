from typing import Any

from ..core import one_of
from ..core.fp import Good, OneOf
from ..core.issue import Issue
from ..core.json import get
from .api import graphql
from .ci import create_ci_query


def get_pr_info(
    token: str,
    owner: str,
    repo: str,
    pr_number: int,
    file_count: int,
) -> OneOf[Issue, Any]:
    """Retrieve the information of the given Github PR."""
    query = create_ci_query(pr_number, False, False)
    variables = {
        'owner': owner,
        'repo': repo,
        'pr': pr_number,
        'fc': file_count,
    }
    return one_of(
        lambda: [
            data
            for res in graphql(token, query, variables)
            for data in get(res, 'repository.pullRequest')
        ],
    )


def get_latest_release(
    token: str,
    owner: str,
    repo: str,
) -> OneOf[Issue, str]:
    """Retrieve the latest release for a repo."""
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
            data
            for res in graphql(token, query, variables)
            for data in get(res, 'repository.releases.nodes.0.tagName')
        ],
    ).flat_map_bad(lambda _: Good('0.0.0'))
