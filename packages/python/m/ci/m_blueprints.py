from pathlib import Path

from m.core import Bad, Res, issue, one_of

from .config import Config, read_config
from .docker.env import MEnvDocker
from .docker.filenames import FileNames


def _write_blueprints(
    config: Config,
    *,
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
        m_tag='"$M_TAG"',
        cache_from_pr='"$CACHE_FROM_PR"',
        base_path=docker_config.base_path,
        registry=docker_config.docker_registry,
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
    update_makefile: bool = False,
    update_workflow: bool = False,
) -> Res[None]:
    """Write a file with the M environment variables.

    Args:
        m_dir: The directory with the m configuration.

    Returns:
        An issue or the m environment instance.
    """
    blueprints_dir = Path(f'{m_dir}/.m/blueprints')
    if not blueprints_dir.exists():
        Path(f'{m_dir}/.m/blueprints/local').mkdir(parents=True)
        Path(f'{m_dir}/.m/blueprints/ci/manifests').mkdir(parents=True)
    return one_of(lambda: [
        None
        for config in read_config(m_dir)
        for _ in _write_blueprints(
            config,
            update_makefile=update_makefile,
            update_workflow=update_workflow,
        )
    ])
