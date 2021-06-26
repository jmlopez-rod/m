import re
from typing import List, Optional, Any
from ..core.fp import OneOf, one_of, Good
from ..core.issue import Issue
from ..core.json import get
from .api import graphql
from .ci_dataclasses import (
    Release,
    PullRequest,
    CommitInfo,
    Commit,
    Author,
    AssociatedPullRequest,
    GithubCiRunInfo,
)
from .ci_graph_queries import commit_query, PULL_REQUEST, LATEST_RELEASE


def create_ci_query(
    pr_number: Optional[int] = None,
    include_commit: bool = None,
    include_release: bool = False,
) -> str:
    """Create github graphql query."""
    items: List[str] = []
    params: List[str] = ['$owner: String!', '$repo: String!']
    if include_commit:
        include_pr = pr_number is None
        items.append(commit_query(include_pr, True))
        params.append('$sha: String')
    if pr_number:
        items.append(PULL_REQUEST)
        params.append('$pr: Int!')
        params.append('$fc: Int!')
    if include_release:
        items.append(LATEST_RELEASE)
    items_str = '\n'.join(items)
    params_str = ', '.join(params)
    return f'''query ({params_str}) {{
      repository(owner:$owner, name:$repo) {{
        {items_str}
      }}
    }}'''


def _parse_commit_message(msg: str, sha: str) -> str:
    match = re.match(r'^Merge (.*) into (.*)$', msg)
    if match:
        return match.groups()[0]
    return sha


def get_build_sha(
    token: str,
    owner: str,
    repo: str,
    sha: str
) -> OneOf[Issue, str]:
    """When building prs, we are not given the actual sha of the commit.
    Instead, we get the sha of the merge commit. This will give us the sha
    that we are looking for."""
    params = ['$owner: String!', '$repo: String!', '$sha: String!']
    params_str = ', '.join(params)
    query = f'''query ({params_str}) {{
      repository(owner:$owner, name:$repo) {{
        {commit_query(False, False)}
      }}
    }}'''
    variables = dict(
        owner=owner,
        repo=repo,
        sha=sha,
    )
    return one_of(lambda: [
        _parse_commit_message(data, sha)
        for res in graphql(token, query, variables)
        for data in get(res, 'repository.commit.message')
    ])


def get_raw_ci_run_info(
    token: str,
    commit_info: CommitInfo,
    pr_number: Optional[int],
    file_count: int,
    include_release: bool
) -> OneOf[Issue, Any]:
    """Retrieve the information of the given Github PR."""
    query = create_ci_query(pr_number, True, include_release)
    owner, repo, sha = [commit_info.owner, commit_info.repo, commit_info.sha]
    variables = dict(owner=owner, repo=repo, sha=sha, fc=file_count)
    if pr_number:
        variables['pr'] = pr_number
    return one_of(lambda: [
        data
        for variables['sha'] in get_build_sha(token, owner, repo, sha)
        for res in graphql(token, query, variables)
        for data in get(res, 'repository')
    ])


def _get_release(raw: Any) -> OneOf[Issue, Optional[Release]]:
    releases = raw.get('releases')
    if releases:
        nodes = releases.get('nodes')
        if nodes and len(nodes) > 0:
            node = nodes[0]
            return Good(Release(
                node['name'],
                node['tagName'],
                node['publishedAt'],
            ))
    return Good(None)


def _get_commit(owner: str, repo: str, raw: Any) -> OneOf[Issue, Commit]:
    commit = raw['commit']
    sha = commit['oid']
    info = Commit(
        author_login=get(commit, 'author.user.login').get_or_else(''),
        short_sha=sha[:7],
        sha=sha,
        message=commit['message'],
        url=f'https://github.com/{owner}/{repo}/commit/{sha}'
    )
    nodes = get(commit, 'associatedPullRequests.nodes').get_or_else([])
    if len(nodes) > 0:
        pr = nodes[0]
        author = pr['author']
        info.associated_pull_request = AssociatedPullRequest(
            author=Author(
                login=author['login'],
                avatar_url=author['avatarUrl'],
                email=author['email'],
            ),
            merged=pr['merged'],
            number=pr['number'],
            base_ref_name=pr['baseRefName'],
            base_ref_oid=pr['baseRefOid'],
            head_ref_name=pr['headRefName'],
            head_ref_oid=pr['headRefOid'],
            title=pr['title'],
            body=pr['body'],
        )
    return Good(info)


def _get_pull_request(
    raw: Any,
    pr_number: Optional[int]
) -> OneOf[Issue, Optional[PullRequest]]:
    pr = raw.get('pullRequest')
    if not pr:
        return Good(None)
    author = pr['author']
    return Good(PullRequest(
        author=Author(
            login=author['login'],
            avatar_url=author['avatarUrl'],
            email=author['email'],
        ),
        pr_number=pr_number or 0,
        pr_branch=pr['headRefName'],
        target_branch=pr['baseRefName'],
        target_sha=pr['baseRefOid'],
        url=pr['url'],
        title=pr['title'],
        body=pr['body'],
        file_count=pr['files']['totalCount'],
        files=[x['path'] for x in pr['files']['nodes']],
        is_draft=pr['isDraft']
    ))


def get_ci_run_info(
    token: str,
    commit_info: CommitInfo,
    pr_number: Optional[int],
    file_count: int,
    include_release: bool
) -> OneOf[Issue, GithubCiRunInfo]:
    """Transform the result from get_raw_ci_run_info to a GithubCiRunInfo."""
    raw_res = get_raw_ci_run_info(
        token,
        commit_info,
        pr_number,
        file_count,
        include_release)
    return one_of(lambda: [
        GithubCiRunInfo(commit, pr, release)
        for raw in raw_res
        for release in _get_release(raw)
        for commit in _get_commit(commit_info.owner, commit_info.repo, raw)
        for pr in _get_pull_request(raw, pr_number)
    ])
