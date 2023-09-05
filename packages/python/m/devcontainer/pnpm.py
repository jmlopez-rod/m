import os
import shutil
from pathlib import Path

from m.core import Bad, Good, Res, issue
from m.core import subprocess as sub
from m.log import Logger
from pydantic import BaseModel

logger = Logger('m.devcontainer.pnpm')

# list of commands that need to be executed in the mounted volume
PNPM_MOUNTED_COMMANDS = (
    'add',
    'i',
    'install',
    'ln',
    'link',
    'prune',
    'rm',
    'remove',
    'unlink',
    'up',
    'update',
)
SUGGESTION = 'suggestion'


def create_symlink(link: Path, source: Path) -> None:
    """Create a symlink that is linked to a source.

    This is a destructive operation - if the link exists it will be removed.

    Args:
        link: The path to the link.
        source: The path to the source.
    """
    if link.exists() or link.is_symlink():
        link.unlink()
    link.symlink_to(source)


class PnpmSetupSummary(BaseModel):
    """Summary of the pnpm setup operation."""

    node_modules: str
    package: str
    npmrc: str
    pnpm_lock: str | None


def _setup_node_modules(work_dir: str, pnpm_dir: str) -> Res[str]:
    work_node_modules = Path(work_dir) / 'node_modules'
    pnpm_node_modules = Path(pnpm_dir) / 'node_modules'

    if work_node_modules.exists() and not work_node_modules.is_symlink():
        # if we remove the directory from inside the container it will take
        # a while, better let the developer do it from the host.
        return issue('non_devcontainer_setup', context={
            'work_node_modules': str(work_node_modules),
            'pnpm_node_modules': str(pnpm_node_modules),
            SUGGESTION: [
                'stop devcontainer',
                'remove all node_modules found in the project directory',
                'reopen project in devcontainer',
            ],
        })

    pnpm_node_modules.mkdir(exist_ok=True)
    create_symlink(work_node_modules, pnpm_node_modules)
    return Good(f'{work_node_modules} -> {pnpm_node_modules}')


def _setup_package(work_dir: str, pnpm_dir: str) -> Res[str]:
    work_package = Path(work_dir) / 'package.json'
    pnpm_package = Path(pnpm_dir) / 'package.json'
    if not work_package.exists():
        return issue('missing_package_json', context={
            'work_dir': str(work_dir),
            SUGGESTION: [
                'directory does not have package.json',
                'you may create one with pnpm init',
            ],
        })
    # ensure the pnpm directory exists otherwise symlink will fail
    Path(pnpm_dir).mkdir(parents=True, exist_ok=True)
    create_symlink(pnpm_package, work_package)
    return Good(f'{pnpm_package} -> {work_package}')


def _setup_npmrc(work_dir: str, pnpm_dir: str) -> Res[str]:
    npmrc_pnpm = Path(pnpm_dir) / '.npmrc'
    npmrc_work = Path(work_dir) / '.npmrc'
    npmrc_home = Path(os.environ.get('HOME', 'undefined')) / '.npmrc'
    npmrc_path = npmrc_work if npmrc_work.exists() else npmrc_home
    if not npmrc_path.exists():
        return issue('missing_npmrc', context={
            'npmrc_work': f'MISSING {npmrc_work}',
            'npmrc_home': f'MISSING {npmrc_home}',
        })
    create_symlink(npmrc_pnpm, npmrc_path)
    return Good(f'{npmrc_pnpm} -> {npmrc_path}')


def pnpm_setup(work_dir: str, pnpm_dir: str) -> Res[None]:
    """Create symbolic links to a mounted volume.

    This is done so that pnpm may take advantage of the cache associated with
    a single pnpm store. When we execute `pnpm install` in the devcontainer
    we want to make sure that other containers may be able to share the pnpm
    cache. To do this we need all containers to use the same pnpm store.

    Args:
        work_dir: The directory where the project is mounted.
        pnpm_dir: The directory where the project will execute pnpm commands.

    Returns:
        A `PnpmSetupSummary` instance.
    """
    package_res = _setup_package(work_dir, pnpm_dir)
    if isinstance(package_res, Bad):
        return Bad(package_res.value)
    package_summary = package_res.value

    node_modules_res = _setup_node_modules(work_dir, pnpm_dir)
    if isinstance(node_modules_res, Bad):
        return Bad(node_modules_res.value)
    node_modules_summary = node_modules_res.value

    npmrc_res = _setup_npmrc(work_dir, pnpm_dir)
    if isinstance(npmrc_res, Bad):
        return Bad(npmrc_res.value)
    npmrc_summary = npmrc_res.value

    # perform a few checks with the lock file
    work_lock = Path(work_dir) / 'pnpm-lock.yaml'
    pnpm_lock_summary = None
    if not work_lock.exists():
        pnpm_lock_summary = f'MISSING {work_lock}'
        logger.warning('pnpm_lock_missing', context={
            'work_lock': pnpm_lock_summary,
            SUGGESTION: 'run `pnpm install` to generate the lock file',
        })
    if work_lock.is_symlink():
        pnpm_lock_summary = f'unlinked symlink {work_lock}'
        work_lock.unlink()

    summary = PnpmSetupSummary(
        node_modules=node_modules_summary,
        package=package_summary,
        npmrc=npmrc_summary,
        pnpm_lock=pnpm_lock_summary,
    )
    logger.debug('pnpm_setup_summary', context=summary.model_dump())
    return Good(None)


def _pnpm(work_dir: str, pnpm_dir: str, pnpm_args: list[str]) -> Res[None]:
    """Execute the pnpm command by first switching to the given pnpm directory.

    Args:
        work_dir: The directory where the project is mounted.
        pnpm_dir: The directory where the project will execute pnpm commands.
        pnpm_args: The arguments to pass to pnpm.

    Returns:
        None if successful, otherwise an error message.
    """
    error = None
    if not Path(f'{work_dir}/node_modules').is_symlink():
        error = f'{work_dir}/node_modules is not a symlink'
    elif not Path(f'{pnpm_dir}/.npmrc').is_symlink():
        error = f'{pnpm_dir}/.npmrc is not a symlink'
    if error:
        return issue('invalid_pnpm_setup', context={'error': error})

    os.chdir(pnpm_dir)
    store_path_res = sub.eval_cmd('pnpm store path')
    if isinstance(store_path_res, Bad):
        return Bad(store_path_res.value)
    logger.info('executing_pnpm_in_mounted_volume', context={
        'store_path': store_path_res.value,
        'pnpm_dir': pnpm_dir,
    })

    pnpm_res = sub.exec_pnpm(pnpm_args)
    if isinstance(pnpm_res, Bad):
        return pnpm_res

    work_lock = Path(work_dir) / 'pnpm-lock.yaml'
    pnpm_lock = Path(pnpm_dir) / 'pnpm-lock.yaml'
    if not work_lock.exists():
        shutil.move(str(pnpm_lock), str(work_lock))
    create_symlink(pnpm_lock, work_lock)
    return Good(None)


def _get_workspaces(workdir: str) -> Res[tuple[str, str]]:
    workspace = os.environ.get('MDC_WORKSPACE')
    pnpm_workspace = os.environ.get('MDC_PNPM_WORKSPACE')
    if not workspace or not pnpm_workspace:
        return issue('missing_env_var', context={
            'MDC_WORKSPACE': workspace,
            'MDC_PNPM_WORKSPACE': pnpm_workspace,
            SUGGESTION: 'are you running this command from a devcontainer?',
        })
    if not workdir.startswith(workspace):
        return issue('invalid_devcontainer_pnpm_use', context={
            'workdir': workdir,
            'workspace': workspace,
            'suggestions': [
                'pnpm alias should only be run in the `workspace`',
                'the original `pnpm` may be used by running `command pnpm`',
            ],
        })
    return Good((workspace, pnpm_workspace))


def run_pnpm(pnpm_args: list[str], *, force_cd: bool) -> Res[None]:
    """Execute the pnpm command with the given arguments.

    Args:
        pnpm_args: The arguments to pass to pnpm.
        force_cd: If True, change the working directory to the mounted volume.

    Returns:
        The exit code of the pnpm command.
    """
    workdir = str(Path.cwd())
    workspace_res = _get_workspaces(workdir)
    if isinstance(workspace_res, Bad):
        return Bad(workspace_res.value)

    workspace, pnpm_workspace = workspace_res.value
    pnpm_command = pnpm_args[0] if pnpm_args else None
    is_cd_command = pnpm_command in PNPM_MOUNTED_COMMANDS
    if not force_cd and (not pnpm_command or not is_cd_command):
        pnpm_res = sub.exec_pnpm(pnpm_args)
        if isinstance(pnpm_res, Bad):
            return pnpm_res
        return Good(None)

    if not Path(f'{workdir}/package.json').exists():
        return issue('missing_package_json', context={
            'workdir': workdir,
            'warning': 'run pnpm commands in directories with package.json',
        })
    pnpm_dir = workdir.replace(workspace, pnpm_workspace, 1)
    return _pnpm(workdir, pnpm_dir, pnpm_args)
