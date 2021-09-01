from ..core import one_of, OneOf, issue, Good
from ..core.issue import Issue
from .config import read_config, Workflow, Config
from .. import git


def _verify_branch(
    config: Config,
    branch: str,
    assertion_type: str
) -> OneOf[Issue, int]:
    workflow = config.workflow
    if workflow == Workflow.FREE_FLOW:
        return issue(
            'The free-flow workflow does not support releases',
            include_traceback=False,
        )
    req_branch = None
    if workflow == Workflow.M_FLOW:
        req_branch = config.m_flow.master_branch
    elif workflow == Workflow.GIT_FLOW:
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
            data=dict(workflow=str(workflow)),
            include_traceback=False,
        )
    if branch != req_branch:
        return issue(
            f"invalid branch for '{assertion_type}' using {config.workflow}",
            data=dict(branch=branch, requiredBranch=req_branch),
            include_traceback=False,
        )
    return Good(0)


def assert_branch(assertion_type: str, m_dir: str) -> OneOf[Issue, str]:
    """Make sure git is using the correct branch based on the workflow."""
    return one_of(lambda: [
        ''
        for config in read_config(m_dir)
        for branch in git.get_branch()
        for _ in _verify_branch(config, branch, assertion_type)
    ])
