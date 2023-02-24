from m.core import Good, Issue, OneOf, issue, one_of
from m.log import Logger

from .. import git
from . import config as cfg_mod
from .config import Config

logger = Logger('m.ci.assert_branch')


def _verify_branch(
    config: Config,
    branch: str,
    assertion_type: str,
) -> OneOf[Issue, int]:
    workflow = config.workflow
    logger.info(f'verifying "{branch}" branch', {
        'workflow': str(workflow),
    })

    if config.uses_free_flow():
        return issue(
            'The free-flow workflow does not support releases',
            include_traceback=False,
        )
    req_branch = None
    if config.uses_m_flow():
        req_branch = config.m_flow.master_branch
    elif config.uses_git_flow():
        flow = config.git_flow
        # releases are made from develop branch
        # hotfixes are made from master branch
        req_branch = (
            flow.develop_branch
            if assertion_type == 'release'
            else flow.master_branch
        )
    if not req_branch:
        return issue(
            'invalid m workflow',
            context={'workflow': str(workflow)},
            include_traceback=False,
        )
    if branch != req_branch:
        return issue(
            f"invalid branch for '{assertion_type}' using {config.workflow}",
            context={'branch': branch, 'requiredBranch': req_branch},
            include_traceback=False,
        )
    return Good(0)


def assert_branch(assertion_type: str, m_dir: str) -> OneOf[Issue, Config]:
    """Make sure git is using the correct branch based on the workflow.

    Args:
        assertion_type:
            Either 'release' or 'hotfix'.
        m_dir:
            The directory for the m configuration.

    Returns:
        A OneOf containing `None` or an `Issue`.
    """
    return one_of(lambda: [
        config
        for config in cfg_mod.read_config(m_dir)
        for branch in git.get_branch()
        for _ in _verify_branch(config, branch, assertion_type)
    ])
