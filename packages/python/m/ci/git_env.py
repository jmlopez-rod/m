import re
from dataclasses import dataclass
from typing import List, Optional
from ..core.fp import OneOf, Good
from ..core.issue import Issue, issue
from .config import Config
from ..core.io import EnvVars
from ..github.ci import Commit, PullRequest, Release


@dataclass
class GitEnv:
    """Object to store the git configuration."""
    sha: str
    branch: str
    target_branch: str
    commit: Optional[Commit] = None
    pull_request: Optional[PullRequest] = None
    release: Optional[Release] = None


def get_pr_number(branch: str) -> int:
    """Retrieve the pull request number from the branch name."""
    if 'pull/' in branch:
        parts = branch.split('/')
        return int(parts[parts.index('pull') + 1])
    return 0


def _remove_strings(content: str, words: List[str]) -> str:
    return re.sub('|'.join(words), '', content)


def get_git_env(_config: Config, env_vars: EnvVars) -> OneOf[Issue, GitEnv]:
    """Obtain the git environment by asking Github's API."""
    branch = _remove_strings(env_vars.git_branch, ['refs/heads/', 'heads/'])
    sha = env_vars.git_sha
    git_env = GitEnv(sha, branch, branch)

    # quick exit for local environment
    if not env_vars.ci_env:
        return Good(git_env)

    # total_files = [
    #     len(item.allowed_files)
    #     for _, item in config.release_from.items()]
    # max_files = max(0, *total_files)
    return issue('not done yet')
