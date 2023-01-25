from dataclasses import dataclass
from typing import Any, Mapping, Optional

from m.core import http
from pydantic import BaseModel

from ..core import issue, one_of
from ..core.fp import Good, OneOf
from ..core.issue import Issue


def request(
    token: str,
    endpoint: str,
    method: str = 'GET',
    dict_data: Optional[Any] = None,
) -> OneOf[Issue, Any]:
    """Make an api request to github.

    See::

        - https://docs.github.com/en/rest/overview/resources-in-the-rest-api
        - https://docs.github.com/en/rest/overview/endpoints-available-for-github-apps

    Args:
        token: A github personal access token.
        endpoint: A github api endpoint.
        method: The http method to use. (default 'GET')
        dict_data: A payload if th method if `POST` or `GET`.

    Returns:
        A response from Github.
    """  # noqa
    url = f'https://api.github.com{endpoint}'
    headers = {'authorization': f'Bearer {token}'}
    return http.fetch_json(url, headers, method, dict_data)


def _filter_data(dict_data: Mapping[str, Any]) -> OneOf[Issue, Any]:
    if dict_data.get('errors'):
        return issue(
            'github graphql errors',
            context={'response': dict_data},
        )
    if dict_data.get('data'):
        return Good(dict_data['data'])
    return issue(
        'github response missing data field',
        context={'response': dict_data},
    )


def graphql(
    token: str,
    query: str,
    variables: Mapping[str, Any],
) -> OneOf[Issue, Any]:
    """Make a request to Github's graphql API:

    https://docs.github.com/en/graphql/guides/forming-calls-with-graphql
    """
    data = {'query': query, 'variables': variables or {}}
    return one_of(
        lambda: [
            payload
            for res in request(token, '/graphql', 'POST', data)
            for payload in _filter_data(res)
        ],
    )


def create_release(
    token: str,
    owner: str,
    repo: str,
    version: str,
    branch: Optional[str] = None,
) -> OneOf[Issue, Any]:
    """Send a payload to create a release in github."""
    endpoint = f'/repos/{owner}/{repo}/releases'
    base = 'https://github.com'
    link = f'{base}/{owner}/{repo}/blob/master/CHANGELOG.md#{version}'
    data = {
        'tag_name': version,
        'name': f'{version}',
        'body': f'**See [CHANGELOG]({link}).**',
        'draft': False,
        'prerelease': False,
    }
    if branch:
        data['target_commitish'] = branch
    return request(token, endpoint, 'POST', data)


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
    """Send a payload to create a pull request in github."""
    endpoint = f'/repos/{owner}/{repo}/pulls'
    return request(token, endpoint, 'POST', pr_info.dict())


def merge_pr(
    token: str,
    owner: str,
    repo: str,
    pr_number: int,
    commit_title: str | None,
) -> OneOf[Issue, Any]:
    """Send a payload to merge a pull request in github."""
    endpoint = f'/repos/{owner}/{repo}/pulls/{pr_number}/merge'
    data = {'commit_title': commit_title} if commit_title else {}
    return request(token, endpoint, 'PUT', data)


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

    The valid states are:

    - pending
    - success
    - failure
    - error
    """
    endpoint = f'/repos/{owner}/{repo}/statuses/{sha_info.sha}'
    data = {
        'context': sha_info.context,
        'state': sha_info.state,
        'description': sha_info.description,
    }
    if sha_info.url:
        data['target_url'] = sha_info.url
    return request(token, endpoint, 'POST', data)
