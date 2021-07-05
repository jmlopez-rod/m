from typing import Mapping, Any
from ..core import one_of, issue
from ..core.fp import OneOf, Good
from ..core.issue import Issue
from ..core.http import fetch_json


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
    url = 'https://api.github.com/graphql'
    headers = {'authorization': f'Bearer {token}'}
    data = dict(query=query, variables=variables or {})
    return one_of(lambda: [
        payload
        for res in fetch_json(url, headers, 'POST', data)
        for payload in _filter_data(res)
    ])
