from functools import partial
from typing import Any, Callable

from m.core import Issue, OneOf, one_of
from m.core.json import get
from m.pydantic import CamelModel
from pydantic import BaseModel, parse_obj_as

from ..api import graphql
from ..enums import MergeableState, PullRequestReviewState
from ..generics import G_Item, WithNodes, identity


class Actor(BaseModel):
    """An object representing a committer."""

    login: str


class PullRequestReview(BaseModel):
    """A review object for a given pull request."""

    author: Actor
    body: str
    state: PullRequestReviewState


class PullRequest(CamelModel):
    """A repository pull request."""

    closed: bool
    title: str
    number: int
    base_ref_name: str
    mergeable: MergeableState
    merged: bool
    author: Actor
    latest_reviews: WithNodes[PullRequestReview]
    url: str


def _fetch(
    transform: Callable[[Any], G_Item],
    token: str,
    owner: str,
    repo: str,
    branch: str,
) -> OneOf[Issue, G_Item]:
    """Retrieve the pr information for the specified branch.

    Args:
        transform: Function to apply to the graphql result.
        token: A Github PAT.
        owner: The owner of the repo.
        repo: The name of the repo.
        branch: Name of the branch.

    Returns:
        A list of pull requests connected to the branch or an issue.
    """
    query = """query ($owner: String!, $repo: String!, $branch: String!) {
        repository(owner:$owner, name:$repo) {
            pullRequests(first: 2, headRefName: $branch) {
                nodes {
                    closed
                    title
                    number
                    baseRefName
                    mergeable
                    merged
                    author {
                        login
                    }
                    latestReviews(last: 10) {
                        nodes {
                            author {
                                login
                            }
                            body
                            state
                        }
                    }
                    url
                }
            }
        }
    }"""
    variables = {'owner': owner, 'repo': repo, 'branch': branch}
    return one_of(
        lambda: [
            transform(pull_requests)
            for res in graphql(token, query, variables)
            for pull_requests in get(res, 'repository.pullRequests.nodes')
        ],
    )


fetch_raw = partial(_fetch, identity)


def fetch(
    token: str,
    owner: str,
    repo: str,
    branch: str,
) -> OneOf[Issue, list[PullRequest]]:
    """Retrieve the pr information for the specified branch.

    Args:
        token: A Github PAT.
        owner: The owner of the repo.
        repo: The name of the repo.
        branch: Name of the branch.

    Returns:
        A list of pull requests connected to the branch or an issue.
    """
    return _fetch(
        lambda raw: parse_obj_as(list[PullRequest], raw),
        token,
        owner,
        repo,
        branch,
    )
