from typing import Mapping, Any
from .core.fp import OneOf, Good, one_of
from .core.issue import Issue, issue
from .core.http import fetch_json
from .core.json import get


def compare_sha_url(owner: str, repo: str, prev: str, next_: str) -> str:
    """Provide a url to compare two sha/tags in a github repo."""
    return f'https://github.com/{owner}/{repo}/compare/{prev}...{next_}'


def _filter_data(data: Mapping[str, Any]) -> OneOf[Issue, Any]:
    if data.get('data'):
        return Good(data['data'])
    return issue('', data={'response': data})


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


def get_pr_info(
    token: str,
    owner: str,
    repo: str,
    pr_number: int,
    file_count: int
) -> OneOf[Issue, Any]:
    """Retrieve the information of the given Github PR."""
    query = '''query ($owner: String!, $repo: String!, $pr: Int!, $fc: Int!) {
      repository(name: $repo, owner: $owner) {
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
      }
    }'''
    variables = dict(
        owner=owner,
        repo=repo,
        pr=pr_number,
        fc=file_count,
    )
    return one_of(lambda: [
        data
        for res in graphql(token, query, variables)
        for data in get(res, 'repository.pullRequest')
    ])
