import re
from dataclasses import dataclass
from typing import List, Optional, cast

from ..github.ci_dataclasses import GithubCiRunInfo
from ..core.fp import OneOf, Good
from ..core.issue import Issue, issue
from .config import Config
from ..core.io import EnvVars
from ..github.ci import (
    Commit, CommitInfo, PullRequest, Release, get_ci_run_info
)


@dataclass
class GitEnv:
    """Object to store the git configuration."""
    sha: str
    branch: str
    target_branch: str
    commit: Optional[Commit] = None
    pull_request: Optional[PullRequest] = None
    release: Optional[Release] = None


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
        for _, item in config.release_from.items()]
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
