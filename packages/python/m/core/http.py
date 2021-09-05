import http.client as httplib
import json
from typing import Any, Mapping, Optional
from urllib.parse import urlparse

from . import issue, one_of
from .fp import Good, OneOf
from .issue import Issue
from .json import parse_json


def get_connection(protocol: str, hostname: str) -> httplib.HTTPConnection:
    """Create a connection for the given host."""
    if protocol == 'https':
        return httplib.HTTPSConnection(hostname)
    return httplib.HTTPConnection(hostname)


def fetch(
    url: str,
    headers: Mapping[str, str],
    method: str = 'GET',
    body: Optional[str] = None,
) -> OneOf[Issue, str]:
    """Send an http(s) request."""
    parts = urlparse(url)
    protocol, hostname, path = [parts.scheme, parts.netloc, parts.path]
    if parts.query:
        path += f'?{parts.query}'
    _headers = {'user-agent': 'm', **headers}
    if body:
        _headers['content-length'] = f'{len(body)}'
    connection = get_connection(protocol, hostname)
    url = f'{hostname}{path}'
    try:
        connection.request(method, path, body, _headers)
    except Exception as ex:
        return issue(
            f'{protocol} request failure',
            cause=ex,
            data=dict(url=url),
        )
    try:
        res = connection.getresponse()
        code = res.status
        res_body = res.read()
        if 200 <= code < 300:
            return Good(res_body)
        return issue(
            f'{protocol} request failure ({code})',
            data=dict(url=url, body=body, code=code, res_body=str(res_body)),
        )
    except Exception as ex:
        return issue(
            f'{protocol} request read failure',
            cause=ex,
            data=dict(url=url),
        )


def fetch_json(
    url: str,
    headers: Mapping[str, str],
    method: str = 'GET',
    data: Any = None,
) -> OneOf[Issue, Any]:
    """Especialized fetch to deal with json data."""
    body = json.dumps(data) if data else None
    _headers = {
        'accept': 'application/json',
        'content-type': 'application/json',
        **headers,
    }
    return one_of(
        lambda: [
            value
            for payload in fetch(url, _headers, method, body)
            for value in parse_json(payload)
        ],
    )
