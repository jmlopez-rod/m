import re
from dataclasses import dataclass
from typing import List, Optional, cast

from ..github.ci_dataclasses import GithubCiRunInfo
from ..core import issue
from ..core.fp import OneOf, Good
from ..core.issue import Issue
from .config import Config, ReleaseFrom
from ..core.io import EnvVars, JsonStr
from ..github.ci import (
    Commit, CommitInfo, PullRequest, Release, get_ci_run_info
)


@dataclass
class GitEnv(JsonStr):
    """Object to store the git configuration."""
    sha: str
    branch: str
    target_branch: str
    commit: Optional[Commit] = None
    pull_request: Optional[PullRequest] = None
    release: Optional[Release] = None

    def get_pr_branch(self) -> str:
        """Get the pull request branch or empty string"""
        return self.pull_request.pr_branch if self.pull_request else ''

    def get_pr_number(self) -> int:
        """Get the pull request branch or 0 if not a pull request"""
        return self.pull_request.pr_number if self.pull_request else 0

    def is_release(self, release_from: Optional[ReleaseFrom]) -> bool:
        """Determine if the current commit should create a release."""
        if not self.commit:
            return False
        return self.commit.is_release(release_from)

    def is_release_pr(self, release_from: Optional[ReleaseFrom]) -> bool:
        """Determine if the the current pr is a release pr."""
        if not self.pull_request:
            return False
        return self.pull_request.is_release_pr(release_from)

    def verify_release_pr(
        self,
        release_from: Optional[ReleaseFrom]
    ) -> OneOf[Issue, int]:
        """Verify the release pull request by applying the rules in the
        release_from object."""
        if not self.pull_request:
            return Good(0)
        return self.pull_request.verify_release_pr(release_from)

    def get_build_tag(
        self,
        config_version: str,
        run_id: str,
        release_from: Optional[ReleaseFrom],
    ) -> OneOf[Issue, str]:
        """Obtain the build tag for the current commit.

        It is tempting to use the config_version when creating a build tag for
        pull requests or branches. This will only be annoying when testing.

        Consider the following scenario. An application is being tested with
        `1.0.1-pr99.b123`. When using docker you may want to refer to the
        latest pr build by using `1.0.1-pr99`. Now lets say that a release
        happened and now the config_version is at `1.1.0`. The application
        build will not get the latest changes because the new changes are in
        `1.1.0-pr99`.

        There are two solutions, either always state the version that is
        being used or make a tag to depend only on the pull request number.
        This is the reason why for prs (constantly changing) we avoid
        using the version in the configuration.

        For release prs we use `rc` followed by the pull request. In this case
        it is safe to use config_version given that there should only be
        one release at a time.
        """
        if not run_id:
            return Good(f'0.0.0-local.{self.sha}')
        if self.is_release(release_from):
            return Good(config_version)
        if self.pull_request:
            pr_number = self.pull_request.pr_number
            if self.is_release_pr(release_from):
                return Good(f'{config_version}-rc{pr_number}.b{run_id}')
            return Good(f'0.0.0-pr{pr_number}.b{run_id}')
        return Good(f'0.0.0-{self.target_branch}.b{run_id}')


def get_pr_number(branch: str) -> Optional[int]:
    """Retrieve the pull request number from the branch name."""
    if 'pull/' in branch:
        parts = branch.split('/')
        return int(parts[parts.index('pull') + 1])
    return None


def _remove_strings(content: str, words: List[str]) -> str:
    return re.sub('|'.join(words), '', content)


def get_git_env(config: Config, env_vars: EnvVars) -> OneOf[Issue, GitEnv]:
    """Obtain the git environment by asking Github's API."""
    branch = _remove_strings(env_vars.git_branch, ['refs/heads/', 'heads/'])
    sha = env_vars.git_sha
    git_env = GitEnv(sha, branch, branch)

    # quick exit for local environment
    if not env_vars.ci_env:
        return Good(git_env)

    total_files = [
        len(item.allowed_files)
        for _, item in config.release_from_dict.items()]
    max_files = max(0, 0, *total_files)
    pr_number = get_pr_number(branch)
    git_env_box = get_ci_run_info(
        token=env_vars.github_token,
        commit_info=CommitInfo(
            owner=config.owner,
            repo=config.repo,
            sha=env_vars.git_sha,
        ),
        pr_number=pr_number,
        file_count=max_files,
        include_release=True,
    )
    if git_env_box.is_bad:
        return issue('git_env failure', cause=cast(Issue, git_env_box.value))

    res = cast(GithubCiRunInfo, git_env_box.value)
    pr = res.pull_request
    git_env.sha = res.commit.sha
    git_env.target_branch = pr.target_branch if pr else branch
    git_env.commit = res.commit
    git_env.pull_request = res.pull_request
    git_env.release = res.release
    return Good(git_env)
