import json as builtin_json
from http import client as httplib
from typing import Any, Mapping, Optional
from urllib.parse import urlparse

from . import Issue, issue, one_of
from .fp import Good, OneOf
from .json import parse_json

STATUS_OK = 200
STATUS_REDIRECT = 300


def _get_connection(protocol: str, hostname: str) -> httplib.HTTPConnection:
    if protocol == 'https':
        return httplib.HTTPSConnection(hostname)  # noqa: S309
    return httplib.HTTPConnection(hostname)


def fetch(
    url: str,
    headers: Mapping[str, str],
    method: str = 'GET',
    body: Optional[str] = None,
) -> OneOf[Issue, str]:
    """Send an http(s) request.

    Args:
        url:
            The url to request.
        headers:
            The headers for the request. By default it sets the `user-agent`
            to "m".
        method:
            The request method type. Defaults to `GET`.
        body:
            The body of the request.

    Returns:
        A `OneOf` containing the raw response from the server or an Issue.
    """
    parts = urlparse(url)
    protocol, hostname, path = [parts.scheme, parts.netloc, parts.path]
    path = f'{path}?{parts.query}' if parts.query else path
    fetch_headers = {'user-agent': 'm', **headers}
    if body:
        fetch_headers['content-length'] = str(len(body))
    connection = _get_connection(protocol, hostname)
    ctxt = {'url': f'{hostname}{path}'}
    # See the next link for explanation disabling WPS440:
    #  https://github.com/wemake-services/wemake-python-styleguide/issues/1416
    try:
        connection.request(method, path, body, fetch_headers)
    except Exception as ex:
        return issue(f'{protocol} request failure', cause=ex, context=ctxt)
    try:
        res = connection.getresponse()
    except Exception as ex:  # noqa: WPS440
        return issue(f'{protocol} response failure', cause=ex, context=ctxt)
    try:
        res_body = res.read()
    except Exception as ex:  # noqa: WPS440
        return issue(f'{protocol} read failure', cause=ex, context=ctxt)
    code = res.getcode()
    if STATUS_OK <= code < STATUS_REDIRECT:
        return Good(res_body)
    return issue(
        f'{protocol} request failure ({code})',
        context={
            'body': body,
            'code': code,
            'res_body': str(res_body),
            **ctxt,
        },
    )


def fetch_json(
    url: str,
    headers: Mapping[str, str],
    method: str = 'GET',
    body_json: Any = None,
) -> OneOf[Issue, Any]:
    """Especialized fetch to deal with json data.

    Args:
        url:
            The url to request.
        headers:
            Additional headers for the request. By default it will add
            proper accept and content-type headers for json requests.
        method:
            The request method type. Defaults to `GET`.
        body_json:
            The data to send to the server (python object).

    Returns:
        A `OneOf` containing a json parsed response from the server or an
        Issue.
    """
    body = builtin_json.dumps(body_json) if body_json else None
    fetch_headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        **headers,
    }
    return one_of(lambda: [
        response
        for payload in fetch(url, fetch_headers, method, body)
        for response in parse_json(payload)
    ])
