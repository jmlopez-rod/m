from typing import Any

from m.core import Issue, OneOf, http


def request(
    token: str,
    endpoint: str,
    method: http.HttpMethod = http.HttpMethod.get,
    dict_data: object | None = None,
) -> OneOf[Issue, Any]:
    """Make an api request to github.

    See::

        - https://docs.github.com/en/rest/overview/resources-in-the-rest-api
        - https://docs.github.com/en/rest/overview/endpoints-available-for-github-apps

    Args:
        token: A github personal access token.
        endpoint: A github api endpoint.
        method: The http method to use. (default 'GET')
        dict_data: A payload if the method if `POST` or `GET`.

    Returns:
        A response from Github.
    """
    url = f'https://api.github.com{endpoint}'
    headers = {'authorization': f'Bearer {token}'}
    return http.fetch_json(url, headers, method, dict_data)
