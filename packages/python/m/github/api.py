from typing import Mapping, Any, Optional
from ..core import one_of, issue
from ..core.fp import OneOf, Good
from ..core.issue import Issue
from ..core.http import fetch_json


def request(
    token: str,
    endpoint: str,
    method: str = 'GET',
    data: Optional[Any] = None,
) -> OneOf[Issue, Any]:
    """Make an api request to github. See:
    - https://docs.github.com/en/rest/overview/resources-in-the-rest-api
    - https://docs.github.com/en/rest/overview/endpoints-available-for-github-apps
    """  # noqa
    url = f'https://api.github.com{endpoint}'
    headers = {'authorization': f'Bearer {token}'}
    return fetch_json(url, headers, method, data)


def _filter_data(data: Mapping[str, Any]) -> OneOf[Issue, Any]:
    if data.get('data'):
        return Good(data['data'])
    return issue('github response missing data field', data={'response': data})


def graphql(
    token: str,
    query: str,
    variables: Mapping[str, Any]
) -> OneOf[Issue, Any]:
    """Make a request to Github's graphql API:

    https://docs.github.com/en/graphql/guides/forming-calls-with-graphql
    """
    data = dict(query=query, variables=variables or {})
    return one_of(lambda: [
        payload
        for res in request(token, '/graphql', 'POST', data)
        for payload in _filter_data(res)
    ])


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
