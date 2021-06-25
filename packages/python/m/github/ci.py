from dataclasses import dataclass
from typing import List, Optional, Any
from ..core.fp import OneOf, one_of
from ..core.issue import Issue
from ..core.json import get
from .api import graphql


_COMMIT = """
  commit: object(expression: $sha) {
    ... on Commit {
      associatedPullRequests(first: 1) {
        nodes {
          author {
            login
            avatarUrl(size: 50)
            ... on User {
              email
            }
          }
          number
          title
          body
          baseRefName
          baseRefOid
          headRefName
          headRefOid
          merged
        }
      }
      author {
        name
        email
        user {
          login
        }
      }
      abbreviatedOid
      message
      url
    }
  }
"""

_LATEST_RELEASE = """
  releases(last: 1) {
    nodes {
      name
      tagName
      publishedAt
    }
  }
"""

_PULL_REQUEST = """
  pullRequest(number: $pr) {
    headRefName
    headRefOid
    baseRefName
    baseRefOid
    title
    body
    url
    author {
      login
      avatarUrl(size: 50)
      ... on User {
        email
      }
    }
    files(first: $fc) {
      totalCount
      nodes {
        path
      }
    }
    isDraft
  }
"""


def create_ci_query(
    pr_number: Optional[int] = None,
    include_commit: bool = None,
    include_release: bool = False,
) -> str:
    """Create github graphql query."""
    items: List[str] = []
    params: List[str] = ['$owner: String!', '$repo: String!']
    if include_commit:
        items.append(_COMMIT)
        params.append('$sha: String')
    if pr_number:
        items.append(_PULL_REQUEST)
        params.append('$pr: Int!')
        params.append('$fc: Int!')
    if include_release:
        items.append(_LATEST_RELEASE)
    items_str = '\n'.join(items)
    params_str = ', '.join(params)
    return f'''query ({params_str}) {{
      repository(owner:$owner, name:$repo) {{
        {items_str}
      }}
    }}'''


@dataclass
class Author:
    """An object representing a commiter."""
    login: str
    avatar_url: str
    email: str


@dataclass
class AssociatedPullRequest:
    """Information for commits that are associated with a pull request."""
    # pylint: disable=too-many-instance-attributes
    author: Author
    merged: bool
    number: int
    base_ref_name: str
    base_ref_oid: str
    head_ref_name: str
    head_ref_oid: str
    title: str
    body: str


@dataclass
class Commit:
    """The git commit info."""
    author_login: str
    short_sha: str
    message: str
    url: str
    associated_pull_request: AssociatedPullRequest


@dataclass
class PullRequest:
    """Pull request information."""
    # pylint: disable=too-many-instance-attributes
    author: Author
    pr_number: int
    pr_branch: str
    target_branch: str
    url: str
    title: str
    body: str
    file_count: int
    files: List[str]
    is_draft: bool


@dataclass
class Release:
    """Github release <==> Git tag."""
    name: str
    tag_name: str
    published_at: str


@dataclass
class GithubCiRunInfo:
    """The main information we need for a ci run."""
    commit: Commit
    pull_request: Optional[PullRequest] = None
    releases: Optional[List[Release]] = None


@dataclass
class CommitInfo:
    """A commit can be tracked with the following properties."""
    owner: str
    repo: str
    sha: str


def get_ci_run_info(
    token: str,
    commit_info: CommitInfo,
    pr_number: Optional[int],
    file_count: int,
    include_release: bool
) -> OneOf[Issue, Any]:
    """Retrieve the information of the given Github PR."""
    query = create_ci_query(pr_number, True, include_release)
    variables = dict(
        owner=commit_info.owner,
        repo=commit_info.repo,
        sha=commit_info.sha,
        fc=file_count,
    )
    if pr_number:
        variables['pr'] = pr_number
    return one_of(lambda: [
        data
        for res in graphql(token, query, variables)
        for data in get(res, 'repository')
    ])
