import re
from typing import Any, Optional

from m.core import Good, Issue, OneOf, non_issue, one_of

from ..core.json import get
from .ci_dataclasses import (
    AssociatedPullRequest,
    Author,
    Commit,
    CommitInfo,
    GithubCiRunInfo,
    PullRequest,
    Release,
)
from .ci_graph_queries import LATEST_RELEASE, PULL_REQUEST, commit_query
from .graphql import api


def create_ci_query(
    pr_number: int | None = None,
    include_commit: bool = False,
    include_release: bool = False,
) -> str:
    """Create github graphql query.

    The information provided is done via presets.

    Args:
        pr_number: If included, it will add pull request information.
        include_commit: If true, include commit information.
        include_release: If true, include release information.

    Returns:
        A string with the graphql query.
    """
    query_items: list[str] = []
    query_params: list[str] = ['$owner: String!', '$repo: String!']
    if include_commit:
        include_pr = pr_number is None
        query_items.append(commit_query(include_pr, include_author=True))
        query_params.append('$sha: String')
    if pr_number:
        query_items.append(PULL_REQUEST)
        query_params.append('$pr: Int!')
        query_params.append('$fc: Int!')
    if include_release:
        query_items.append(LATEST_RELEASE)
    items_str = '\n'.join(query_items)
    params_str = ', '.join(query_params)
    return f"""query ({params_str}) {{
      repository(owner:$owner, name:$repo) {{
        {items_str}
      }}
    }}"""


def _parse_commit_message(msg: str, sha: str) -> str:
    match = re.match('^Merge (.*) into (.*)$', msg)
    if match:
        return match.groups()[0]
    return sha


def get_build_sha(
    token: str,
    owner: str,
    repo: str,
    sha: str,
) -> OneOf[Issue, str]:
    """Obtain the commit sha in a pull request.

    When building prs, we are not given the actual sha of the commit.

    Instead, we get the sha of the merge commit. This will give us the
    sha that we are looking for.

    Args:
        token: A Github PAT.
        owner: The owner of the repo.
        repo: The name of the repo.
        sha: The merge sha provided by github.

    Returns:
        The actual sha of the commit.
    """
    query_params = ['$owner: String!', '$repo: String!', '$sha: String!']
    params_str = ', '.join(query_params)
    commit_query_str = commit_query(include_pr=False, include_author=False)
    query = f"""query ({params_str}) {{
      repository(owner:$owner, name:$repo) {{
        {commit_query_str}
      }}
    }}"""
    variables = {
        'owner': owner,
        'repo': repo,
        'sha': sha,
    }
    return one_of(
        lambda: [
            _parse_commit_message(commit_msg, sha)
            for res in api.graphql(token, query, variables)
            for commit_msg in get(res, 'repository.commit.message')
        ],
    )


def get_raw_ci_run_info(
    token: str,
    commit_info: CommitInfo,
    pr_number: int | None,
    file_count: int,
    include_release: bool,
    get_sha: bool = True,
) -> OneOf[Issue, Any]:
    """Retrieve the information of the given Github PR.

    Args:
        token: A Github PAT.
        commit_info: The owner, repo and sha.
        pr_number: The pull request number.
        file_count:  The maximum number of files in the pr to retrieve.
        include_release: If true it will provide release information.
        get_sha: If true, it will obtain the actual sha of the commit.

    Returns:
        The Github payload with the raw information.
    """
    query = create_ci_query(
        pr_number,
        include_commit=True,
        include_release=include_release,
    )
    owner, repo, sha = [commit_info.owner, commit_info.repo, commit_info.sha]
    variables = {'owner': owner, 'repo': repo, 'sha': sha, 'fc': file_count}
    if pr_number:
        variables['pr'] = pr_number
    if get_sha:
        build_sha = get_build_sha(token, owner, repo, sha)
        if build_sha.is_bad:
            return build_sha
        variables['sha'] = non_issue(build_sha)
    return one_of(lambda: [
        repo_data
        for res in api.graphql(token, query, variables)
        for repo_data in get(res, 'repository')
    ])


def _get_release(raw: Any) -> OneOf[Issue, Optional[Release]]:
    releases = raw.get('releases')
    if releases:
        nodes = releases.get('nodes')
        if nodes:
            node = nodes[0]
            return Good(
                Release(
                    name=node['name'],
                    tag_name=node['tagName'],
                    published_at=node['publishedAt'],
                ),
            )
    return Good(None)


def _get_commit(owner: str, repo: str, raw: Any) -> OneOf[Issue, Commit]:
    commit = raw['commit']
    sha = commit['oid']
    commit_info = Commit(
        author_login=get(commit, 'author.user.login').get_or_else(''),
        short_sha=sha[:7],
        sha=sha,
        message=commit['message'],
        url=f'https://github.com/{owner}/{repo}/commit/{sha}',
    )
    nodes = get(commit, 'associatedPullRequests.nodes').get_or_else([])
    if nodes:
        pr = nodes[0]
        author = pr.get('author')
        commit_info.associated_pull_request = AssociatedPullRequest(
            author=Author(**author),
            merged=pr.get('merged'),
            pr_number=pr.get('number'),
            target_branch=pr.get('baseRefName'),
            target_sha=pr.get('baseRefOid'),
            pr_branch=pr.get('headRefName'),
            pr_sha=pr.get('headRefOid'),
            title=pr.get('title'),
            body=pr.get('body'),
        )
    return Good(commit_info)


def _get_pull_request(
    raw: Any,
    pr_number: Optional[int],
) -> OneOf[Issue, Optional[PullRequest]]:
    pr = raw.get('pullRequest')
    if not pr:
        return Good(None)
    author = pr.get('author', {})
    return Good(
        PullRequest(
            author=Author(**author),
            pr_number=pr_number or 0,
            pr_branch=pr.get('headRefName'),
            target_branch=pr.get('baseRefName'),
            target_sha=pr.get('baseRefOid'),
            url=pr.get('url'),
            title=pr.get('title'),
            body=pr.get('body'),
            file_count=pr.get('files', {}).get('totalCount', 0),
            files=[x['path'] for x in pr.get('files', {}).get('nodes', [])],
            is_draft=pr.get('isDraft'),
        ),
    )


def get_ci_run_info(
    token: str,
    commit_info: CommitInfo,
    pr_number: int | None,
    file_count: int,
    include_release: bool,
) -> OneOf[Issue, GithubCiRunInfo]:
    """Transform the result from get_raw_ci_run_info to a GithubCiRunInfo.

    Args:
        token: A Github PAT.
        commit_info: An instance of a commit info.
        pr_number: An optional pull request number.
        file_count: The maximum number of files to report.
        include_release: If true it will provide release information.

    Returns:
        If successful, a `GithubCiRunInfo` instance.
    """
    raw_res = get_raw_ci_run_info(
        token,
        commit_info,
        pr_number,
        file_count,
        include_release,
    )
    return one_of(
        lambda: [
            GithubCiRunInfo(commit=commit, pull_request=pr, release=release)
            for raw in raw_res
            for release in _get_release(raw)
            for commit in _get_commit(commit_info.owner, commit_info.repo, raw)
            for pr in _get_pull_request(raw, pr_number)
        ],
    )


def compare_sha_url(owner: str, repo: str, prev: str, nxt: str) -> str:
    """Generate a url to compare two sha/tags in a github repo.

    Args:
        owner: The repo owner.
        repo: The repo name.
        prev: The previous sha.
        nxt: The next sha.

    Returns:
        A url comparing two shas.
    """
    return f'https://github.com/{owner}/{repo}/compare/{prev}...{nxt}'
