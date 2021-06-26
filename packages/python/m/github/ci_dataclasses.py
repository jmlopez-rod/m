from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Author:
    """An object representing a commiter."""
    login: str
    avatar_url: str
    email: str


@dataclass
class AssociatedPullRequest:
    """Information for commits that are associated with a pull request."""
    # pylint: disable=too-many-instance-attributes
    author: Author
    merged: bool
    number: int
    base_ref_name: str
    base_ref_oid: str
    head_ref_name: str
    head_ref_oid: str
    title: str
    body: str


@dataclass
class Commit:
    """The git commit info."""
    author_login: str
    short_sha: str
    sha: str
    message: str
    url: str
    associated_pull_request: Optional[AssociatedPullRequest] = None


@dataclass
class PullRequest:
    """Pull request information."""
    # pylint: disable=too-many-instance-attributes
    author: Author
    pr_number: int
    pr_branch: str
    target_branch: str
    target_sha: str
    url: str
    title: str
    body: str
    file_count: int
    files: List[str]
    is_draft: bool


@dataclass
class Release:
    """Github release <==> Git tag."""
    name: str
    tag_name: str
    published_at: str


@dataclass
class GithubCiRunInfo:
    """The main information we need for a ci run."""
    commit: Commit
    pull_request: Optional[PullRequest] = None
    release: Optional[Release] = None


@dataclass
class CommitInfo:
    """A commit can be tracked with the following properties."""
    owner: str
    repo: str
    sha: str
