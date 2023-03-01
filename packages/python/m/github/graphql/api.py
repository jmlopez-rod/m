from typing import Any, Mapping

from m.core import Good, Issue, OneOf, http, issue, one_of

from ..request import request

HttpMethod = http.HttpMethod


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
    """Make a request to Github's graphql API.

    https://docs.github.com/en/graphql/guides/forming-calls-with-graphql

    Args:
        token: A github PAT.
        query: A graphql query.
        variables: The variables to use in the query.

    Returns:
        The Github response.
    """
    payload = {'query': query, 'variables': variables or {}}
    return one_of(
        lambda: [
            payload
            for res in request(token, '/graphql', HttpMethod.post, payload)
            for payload in _filter_data(res)
        ],
    )
