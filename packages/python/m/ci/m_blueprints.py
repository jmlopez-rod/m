from pathlib import Path

from m.core import Res, issue, one_of

from .docker.env import MEnvDocker
from .m_env import MEnv, get_m_env


def _write_blueprints(m_env: MEnv) -> Res[None]:
    m_dir = m_env.config.m_dir
    docker_config = m_env.config.docker_config
    if not docker_config:
        return issue(
            'missing docker_config in m file',
            context={'m_dir': m_dir},
        )

    git = m_env.git_env
    associated_pr = (
        git.pull_request or (git.commit and git.commit.associated_pull_request)
    )
    associated_pr_num = associated_pr.pr_number if associated_pr else 0
    env_docker = MEnvDocker(
        m_tag=m_env.release_env.build_tag,
        base_path=docker_config.base_path,
        registry=docker_config.docker_registry,
        pr_number=git.get_pr_number(),
        associated_pr_number=associated_pr_num,
    )
    return docker_config.write_blueprints(m_dir, env_docker)


def write_blueprints(m_dir: str) -> Res[None]:
    """Write a file with the M environment variables.

    Args:
        m_dir: The directory with the m configuration.

    Returns:
        An issue or the m environment instance.
    """
    local_dir = Path(f'{m_dir}/.m/docker-images/local')
    if not local_dir.exists():
        local_dir.mkdir(parents=True)
        Path(f'{m_dir}/.m/docker-images/ci/manifests').mkdir(parents=True)
    return one_of(lambda: [
        None
        for m_env in get_m_env(m_dir)
        for _ in _write_blueprints(m_env)
    ])
