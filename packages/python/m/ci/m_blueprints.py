from pathlib import Path

from m.core import Bad, Res, issue, one_of

from .config import Config, read_config
from .docker.env import MEnvDocker
from .docker.filenames import FileNames


def _write_blueprints(
    config: Config,
    *,
    m_tag: str,
    cache_from_pr: str,
    update_makefile: bool,
    update_workflow: bool,
) -> Res[None]:
    m_dir = config.m_dir
    docker_config = config.docker_config
    if not docker_config:
        return issue(
            'missing docker_config in m file',
            context={'m_dir': m_dir},
        )

    env_docker = MEnvDocker(
        m_tag=m_tag,
        cache_from_pr=cache_from_pr,
        base_path=docker_config.base_path,
        registry=docker_config.docker_registry,
        multi_arch=bool(docker_config.architectures),
        architectures=list((docker_config.architectures or {}).keys()),
        use_buildx=docker_config.platforms is not None,
    )
    files = FileNames.create_instance(m_dir)
    if update_makefile:
        update_res = docker_config.update_makefile(files)
        if isinstance(update_res, Bad):
            return Bad(update_res.value)
    if update_workflow:
        update_res = docker_config.update_github_workflow(files)
        if isinstance(update_res, Bad):
            return Bad(update_res.value)
    return docker_config.write_blueprints(m_dir, env_docker)


def write_blueprints(
    m_dir: str,
    *,
    m_tag: str,
    cache_from_pr: str,
    update_makefile: bool = False,
    update_workflow: bool = False,
) -> Res[None]:
    """Write a file with the M environment variables.

    Args:
        m_dir: The directory with the m configuration.
        m_tag: The unique identifier for the build.
        cache_from_pr: The pr number to attempt to pull cache from.
        update_makefile: If true, updates the `Makefile`.
        update_workflow: If true, updates the github workflow.

    Returns:
        An issue or the m environment instance.
    """
    blueprints_dir = Path(f'{m_dir}/.m/blueprints')
    if not blueprints_dir.exists():
        Path(f'{m_dir}/.m/blueprints/local').mkdir(parents=True)
        Path(f'{m_dir}/.m/blueprints/ci').mkdir(parents=True)
    return one_of(lambda: [
        None
        for config in read_config(m_dir)
        for _ in _write_blueprints(
            config,
            m_tag=m_tag,
            cache_from_pr=cache_from_pr,
            update_makefile=update_makefile,
            update_workflow=update_workflow,
        )
    ])
