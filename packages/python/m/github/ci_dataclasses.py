from dataclasses import dataclass
from typing import Optional, List
from ..core import issue
from ..core.io import JsonStr
from ..core.fp import OneOf, Good
from ..core.issue import Issue
from ..ci.config import ReleaseFrom


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
    target_branch: str
    target_sha: str
    pr_branch: str
    pr_sha: str
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

    def is_release(self, release_from: Optional[ReleaseFrom]) -> bool:
        """Determine if the current commit should create a release."""
        if not release_from:
            return False
        return release_from.pr_branch == self.get_pr_branch()


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

    def is_release_pr(self, release_from: Optional[ReleaseFrom]) -> bool:
        """Determine if the pull request is a release pull request."""
        if not release_from:
            return False
        return release_from.pr_branch == self.pr_branch

    def verify_release(
        self,
        release_from: Optional[ReleaseFrom]
    ) -> OneOf[Issue, int]:
        """Return 0 if everything is ok with the release pr pull request."""
        is_release_pr = self.is_release_pr(release_from)
        if not is_release_pr:
            return Good(0)
        allowed_files: List[str] = []
        if release_from:
            allowed_files = release_from.allowed_files
        err_data = dict(
            allowed_files=allowed_files,
            file_count=self.file_count,
            modified_files=self.files
        )
        if allowed_files and self.file_count > len(allowed_files):
            return issue(
                'max files threshold exceeded in release pr',
                data=err_data)
        if (
            allowed_files and
            not set(self.files).issubset(set(allowed_files))
        ):
            return issue(
                'modified files not subset of the allowed files',
                data=err_data)
        return Good(0)


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
