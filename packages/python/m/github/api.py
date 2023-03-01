from dataclasses import dataclass
from typing import Any, Optional

from m.core import Issue, OneOf, http
from pydantic import BaseModel

from .request import request

HttpMethod = http.HttpMethod


def _repos(owner: str, repo: str, *endpoint: str) -> str:
    return '/'.join(['', 'repos', owner, repo, *endpoint])


def create_release(
    token: str,
    owner: str,
    repo: str,
    version: str,
    branch: str | None = None,
) -> OneOf[Issue, Any]:
    """Send a payload to create a release in github.

    Args:
        token: A github PAT.
        owner: The owner of the repo.
        repo: The name of the repo.
        version: The version that marks the release.
        branch: Optional branch to tag, defaults to the default branch.

    Returns:
        The Github response after a release is created.
    """
    endpoint = _repos(owner, repo, 'releases')
    base = 'https://github.com'
    link = f'{base}/{owner}/{repo}/blob/master/CHANGELOG.md#{version}'
    payload = {
        'tag_name': version,
        'name': f'{version}',
        'body': f'**See [CHANGELOG]({link}).**',
        'draft': False,
        'prerelease': False,
    }
    if branch:
        payload['target_commitish'] = branch
    return request(token, endpoint, HttpMethod.post, payload)


class GithubPullRequest(BaseModel):
    """Data needed to create a pull request."""

    title: str
    body: str
    head: str
    base: str


def create_pr(
    token: str,
    owner: str,
    repo: str,
    pr_info: GithubPullRequest,
) -> OneOf[Issue, Any]:
    """Send a payload to create a pull request in github.

    Args:
        token: A github PAT.
        owner: The owner of the repo.
        repo: The name of the repo.
        pr_info: The pull request information.

    Returns:
        The Github response if successful.
    """
    endpoint = _repos(owner, repo, 'pulls')
    return request(token, endpoint, HttpMethod.post, pr_info.dict())


def merge_pr(
    token: str,
    owner: str,
    repo: str,
    pr_number: int,
    commit_title: str | None,
) -> OneOf[Issue, Any]:
    """Send a payload to merge a pull request in github.

    Args:
        token: A github PAT.
        owner: The owner of the repo.
        repo: The name of the repo.
        pr_number: The number of the pull request.
        commit_title: An optional commit title to use when merging.

    Returns:
        The payload provided by Github if successful.
    """
    endpoint = _repos(owner, repo, 'pulls', str(pr_number), 'merge')
    payload = {'commit_title': commit_title} if commit_title else {}
    return request(token, endpoint, HttpMethod.put, payload)


@dataclass
class GithubShaStatus:
    """Data needed to create a pull request."""

    sha: str
    context: str
    state: str
    description: str
    url: Optional[str] = None


def commit_status(
    token: str,
    owner: str,
    repo: str,
    sha_info: GithubShaStatus,
) -> OneOf[Issue, Any]:
    """Set a status for a sha.

    The valid states are::

    - pending
    - success
    - failure
    - error

    Args:
        token: A github PAT.
        owner: The owner of the repo.
        repo: The name of the repo.
        sha_info: An instance of a `GithubShaStatus`.

    Returns:
        The response from Github after setting a commit status.
    """
    endpoint = _repos(owner, repo, 'statuses', sha_info.sha)
    payload = {
        'context': sha_info.context,
        'state': sha_info.state,
        'description': sha_info.description,
    }
    if sha_info.url:
        payload['target_url'] = sha_info.url
    return request(token, endpoint, HttpMethod.post, payload)
