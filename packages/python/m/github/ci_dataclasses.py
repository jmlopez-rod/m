from typing import List, Optional

from m.pydantic import CamelModel
from pydantic import BaseModel


class Author(CamelModel):
    """An object representing a committer."""

    login: str
    avatar_url: str | None
    email: str | None


class AssociatedPullRequest(BaseModel):
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


class Commit(BaseModel):
    """The git commit info."""

    author_login: str
    short_sha: str
    sha: str
    message: str
    url: str
    associated_pull_request: Optional[AssociatedPullRequest] = None

    def get_pr_branch(self) -> str:
        """Find the git branch if commit has an associated pr.

        Returns:
            The pr branch if the commit has an associated pr or empty
            string.
        """
        if not self.associated_pull_request:
            return ''
        return self.associated_pull_request.pr_branch

    def is_release(self, release_prefix: str | None) -> bool:
        """Determine if the current commit should create a release.

        Args:
            release_prefix: The prefix used to flag a release.

        Returns:
            True if we are dealing with a release branch.
        """
        if not release_prefix:
            return False
        return self.get_pr_branch().startswith(release_prefix)


class PullRequest(BaseModel):
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

    def is_release_pr(self, release_prefix: str | None) -> bool:
        """Determine if the pull request is a release pull request.

        Args:
            release_prefix: The prefix used to flag a release.

        Returns:
            True if we are dealing with a release branch.
        """
        if not release_prefix:
            return False
        return self.pr_branch.startswith(release_prefix)


class Release(BaseModel):
    """Github release <==> Git tag."""

    name: str
    tag_name: str
    published_at: str


class GithubCiRunInfo(BaseModel):
    """The main information we need for a ci run."""

    commit: Commit
    pull_request: Optional[PullRequest] = None
    release: Optional[Release] = None


class CommitInfo(BaseModel):
    """A commit can be tracked with the following properties."""

    owner: str
    repo: str
    sha: str
