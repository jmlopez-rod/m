from m.ci.config import Config, GitFlowConfig, MFlowConfig, Workflow
from m.core.ci_tools import EnvVars

CONFIG = Config(
    owner='jmlopez-rod',
    repo='m',
    version='0.0.0',
    m_dir='m',
    workflow=Workflow.free_flow,
    git_flow=GitFlowConfig(),
    m_flow=MFlowConfig(),
)

ENV_VARS = EnvVars(  # noqa: S106 - testing, token is irrelevant
    ci_env=True,
    github_token='super_secret_like_damn',
    server_url='abc.xyz',
    run_id='404',
    run_number='1',
    run_url='http://abc.xyz/404',
    git_branch='refs/heads/master',
    git_sha='git-sha-abc-123',
)


def mock_commit_sha(sha: str) -> str:
    return f"""{{
        "data": {{
            "repository": {{
                "commit": {{
                    "message": "Merge {sha} into sha2"
                }}
            }}
        }}
    }}"""
