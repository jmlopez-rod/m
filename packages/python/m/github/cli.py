from typing import Any
from ..core.fp import OneOf, one_of
from ..core.issue import Issue
from ..core.json import get
from .api import graphql
from .ci import create_ci_query


def get_pr_info(
    token: str,
    owner: str,
    repo: str,
    pr_number: int,
    file_count: int
) -> OneOf[Issue, Any]:
    """Retrieve the information of the given Github PR."""
    query = create_ci_query(pr_number, False, False)
    variables = dict(
        owner=owner,
        repo=repo,
        pr=pr_number,
        fc=file_count,
    )
    return one_of(lambda: [
        data
        for res in graphql(token, query, variables)
        for data in get(res, 'repository.pullRequest')
    ])
