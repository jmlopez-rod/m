import re
from typing import cast

from m.ci.versioning import VersionInputs, build_m_tag, build_py_tag
from m.core.maybe import maybe
from m.log import EnvVars
from pydantic import BaseModel

from ..core import Issue, issue
from ..core.fp import Good, OneOf
from ..github.ci import (
    Commit,
    CommitInfo,
    PullRequest,
    Release,
    get_ci_run_info,
)
from ..github.ci_dataclasses import GithubCiRunInfo
from .config import Config


def get_release_prefix(config: Config) -> str | None:
    """Find out the release prefix.

    Args:
        config:
            The m configuration. Its workflow is used to determine the prefix.

    Returns:
        The release prefix or None if not using a supported workflow.
    """
    if config.uses_git_flow():
        return config.git_flow.release_prefix
    if config.uses_m_flow():
        return config.m_flow.release_prefix
    return None


def get_hotfix_prefix(config: Config) -> str | None:
    """Find out the hotfix prefix.

    Args:
        config:
            The m configuration. Its workflow is used to determine the prefix.

    Returns:
        The hofix prefix or None if not using a supported workflow.
    """
    if config.uses_git_flow():
        return config.git_flow.hotfix_prefix
    if config.uses_m_flow():
        return config.m_flow.hotfix_prefix
    return None


def _version_inputs(
    git_env: 'GitEnv',
    config: Config,
    run_id: str,
) -> VersionInputs | None:
    is_release = git_env.is_release(config)
    is_release_pr = git_env.is_release_pr(config)
    is_hotfix_pr = git_env.is_hotfix_pr(config)
    is_dev_branch = git_env.target_branch == config.git_flow.develop_branch
    if config.uses_git_flow() and is_dev_branch:
        if is_release or is_release_pr or is_hotfix_pr:
            return None
    pr_number = maybe(lambda: git_env.pull_request.pr_number)  # type: ignore[union-attr]
    return VersionInputs(
        version=config.version,
        version_prefix=_build_tag_prefix(config),
        run_id=run_id,
        sha=git_env.sha,
        pr_number=pr_number,
        branch=git_env.target_branch,
        is_release=is_release,
        is_release_pr=is_release_pr,
        is_hotfix_pr=is_hotfix_pr,
    )


class GitEnv(BaseModel):
    """Object to store the git configuration."""

    sha: str
    branch: str
    target_branch: str
    commit: Commit | None = None
    pull_request: PullRequest | None = None
    release: Release | None = None

    def get_pr_branch(self) -> str:
        """Get the pull request branch or empty string.

        Returns:
            The name of the pull request branch or an empty string when not
            dealing with a pull request.
        """
        return self.pull_request.pr_branch if self.pull_request else ''

    def get_pr_number(self) -> int:
        """Get the pull request number or 0 if not a pull request.

        Returns:
            The pull request number or 0 if not a pull request.
        """
        return self.pull_request.pr_number if self.pull_request else 0

    def is_release(self, config: Config) -> bool:
        """Determine if the current commit should create a release.

        Args:
            config: The `m` configuration.

        Returns:
            True if we are dealing with a release.
        """
        if not self.commit:
            return False
        release_prefix = get_release_prefix(config)
        hotfix_prefix = get_hotfix_prefix(config)
        if config.uses_m_flow() and self.branch != config.m_flow.master_branch:
            return False
        if config.uses_git_flow():
            if self.branch != config.git_flow.master_branch:
                return False
        return (
            self.commit.is_release(release_prefix)
            or self.commit.is_release(hotfix_prefix)
        )

    def is_release_pr(self, config: Config) -> bool:
        """Determine if the the current pr is a release pr.

        Args:
            config: The `m` configuration.

        Returns:
            True if we are dealing with a release pr.
        """
        if not self.pull_request:
            return False
        release_prefix = get_release_prefix(config)
        return self.pull_request.is_release_pr(release_prefix)

    def is_hotfix_pr(self, config: Config) -> bool:
        """Determine if the the current pr is a hotfix pr.

        It is a release pr as far as the pull request should see it but
        from the context of the git environment we need to label it as a
        hotfix pr.

        Args:
            config: The m configuration object.

        Returns:
            True if the we are dealing with hotfix pr.
        """
        if not self.pull_request:
            return False
        hotfix_prefix = get_hotfix_prefix(config)
        return self.pull_request.is_release_pr(hotfix_prefix)

    def get_build_tag(self, config: Config, run_id: str) -> OneOf[Issue, str]:
        """Create a build tag for the current commit.

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
        one release at a time. We treat hotfixes similar to releases.

        Git flow will generate a special build tag: SKIP. This will happen when
        we try to merge a release or hotfix branch to the develop branch.

        Args:
            config: The `m` configuration.
            run_id: A unique identifier for the run/job.

        Returns:
            A unique identifier for the build. This tag is compatible with
            both `npm` and `docker`.
        """
        ver_input = _version_inputs(self, config, run_id)
        if ver_input:
            return Good(build_m_tag(ver_input, config))
        return Good('SKIP')

    def get_py_tag(self, config: Config, run_id: str) -> OneOf[Issue, str]:
        """Create a python tag for the current commit.

        Args:
            config: The `m` configuration.
            run_id: A unique identifier for the run/job.

        Returns:
            A unique identifier for the build. This tag is compatible with
            python.
        """
        ver_input = _version_inputs(self, config, run_id)
        if ver_input:
            return Good(build_py_tag(ver_input, config))
        return Good('SKIP')


def _build_tag_prefix(config: Config) -> str:
    if config.uses_free_flow():
        return ''
    if config.build_tag_with_version:
        ver = config.version.split('-')[0]
        parts = [int(x) for x in ver.split('.')]
        minor_ver = parts[1] + 1
        return f'{parts[0]}.{minor_ver}.0'
    return '0.0.0'


def get_pr_number(branch: str) -> int | None:
    """Retrieve the pull request number from the branch name.

    Args:
        branch: The branch name from where the pr number is extracted.py

    Returns:
        The pr number if the branch is a pull request otherwise `None`.
    """
    if 'pull/' in branch:
        parts = branch.split('/')
        return int(parts[parts.index('pull') + 1])
    return None


def _remove_strings(str_content: str, words: list[str]) -> str:
    return re.sub('|'.join(words), '', str_content)


def get_git_env(config: Config, env_vars: EnvVars) -> OneOf[Issue, GitEnv]:
    """Obtain the git environment by asking Github's API.

    Args:
        config: The m configuration object.
        env_vars: The environment variables.

    Returns:
        The git environment object or an issue.
    """
    branch = _remove_strings(env_vars.git_branch, ['refs/heads/', 'heads/'])
    sha = env_vars.git_sha
    git_env = GitEnv(sha=sha, branch=branch, target_branch=branch)

    # quick exit for local environment
    if not env_vars.ci_env:
        return Good(git_env)

    pr_number = get_pr_number(branch)
    git_env_box = get_ci_run_info(
        token=env_vars.github_token,
        commit_info=CommitInfo(
            owner=config.owner,
            repo=config.repo,
            sha=env_vars.git_sha,
        ),
        pr_number=pr_number,
        file_count=0,
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
