from dataclasses import dataclass
from typing import Optional, List
from ..core.io import JsonStr


@dataclass
class Author(JsonStr):
    """An object representing a commiter."""
    login: str
    avatar_url: str
    email: str


@dataclass
class AssociatedPullRequest(JsonStr):
    """Information for commits that are associated with a pull request."""
    # pylint: disable=too-many-instance-attributes
    author: Author
    merged: bool
    pr_number: int
    base_ref_name: str
    base_ref_oid: str
    pr_branch: str
    head_ref_oid: str
    title: str
    body: str


@dataclass
class Commit(JsonStr):
    """The git commit info."""
    author_login: str
    short_sha: str
    sha: str
    message: str
    url: str
    associated_pull_request: Optional[AssociatedPullRequest] = None

    def get_pr_branch(self) -> str:
        """Returns the pr branch if the commit has an associated pr or empty
        string."""
        if not self.associated_pull_request:
            return ''
        return self.associated_pull_request.pr_branch


@dataclass
class PullRequest(JsonStr):
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
class Release(JsonStr):
    """Github release <==> Git tag."""
    name: str
    tag_name: str
    published_at: str


@dataclass
class GithubCiRunInfo(JsonStr):
    """The main information we need for a ci run."""
    commit: Commit
    pull_request: Optional[PullRequest] = None
    release: Optional[Release] = None


@dataclass
class CommitInfo(JsonStr):
    """A commit can be tracked with the following properties."""
    owner: str
    repo: str
    sha: str
