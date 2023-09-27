import os
from functools import partial
from pathlib import Path
from types import MappingProxyType

from m.color.colors import color
from m.core import Bad, subprocess

from m import git

UNKNOWN = 'unknown'
UNKNOWN_COLOR = '\033[38;5;20m'

COL = partial(color, auto_end=False)

# https://www.compart.com/en/unicode/
# https://gitmoji.dev/
STATUS_SYMBOLS = MappingProxyType({
    UNKNOWN: '🧐',  # contender: ???
    'untracked': '🌱',
    'stash': '\u271A',  # Heavy Greek Cross
    'ahead': '\u25B6',  # Black Right-Pointing Triangle
    'behind': '\u25C0',  # Black Left-Pointing Triangle
    'clean': '\u2714',  # Heavy Check Mark
    'staged': '🌭',  # contender: \u25CF Black Circle
    'dirty': '\u2716',  # Heavy Multiplication X
    'diverged': '💥',  # contender: !
})

STATUS_COLORS = MappingProxyType({
    UNKNOWN: UNKNOWN_COLOR,  # dark blue
    'untracked': '\033[38;5;76m',  # mid lime-green
    'stash': '\033[38;5;76m',  # mid lime-green
    'ahead': '\033[38;5;226m',  # bright yellow
    'behind': '\033[38;5;142m',  # darker yellow-orange
    'clean': '\033[38;5;82m',  # brighter green
    'staged': '\033[38;5;214m',  # orangey yellow
    'dirty': '\033[38;5;202m',  # orange
    'diverged': '\033[38;5;196m',  # red
})


def _branch_display(current_branch: str) -> str:
    # if the branch is HEAD, display the commit hash instead
    if current_branch == 'HEAD':
        short_res = subprocess.eval_cmd('git rev-parse --short HEAD')
        return short_res.get_or_else(current_branch)
    return current_branch


def _branch_sec(branch: str, status: str) -> str:
    s_color = STATUS_COLORS.get(status, UNKNOWN_COLOR)
    s_sym = STATUS_SYMBOLS.get(status, '???')
    branch_info = ''.join([r'\[', s_color, r'\]', f'{s_sym} {branch}'])
    return COL(r'\[{gray}\][', branch_info, r'\[{gray}\]]')


def _repo_info() -> tuple[str, str]:
    repo_path = git.get_repo_path().get_or_else('[UNKNOWN_REPO_PATH]')
    cwd = str(Path.cwd())
    repo = repo_path.split('/')[-1]
    rel_path = cwd.replace(repo_path, '^', 1)
    return repo, rel_path


def _container_info() -> str:
    name = os.environ.get('DK_CONTAINER_NAME', 'devcontainer')
    version = os.environ.get('DK_CONTAINER_VERSION')
    if version:
        dk_version = version.replace('0.0.0-', '')
        if dk_version.startswith('local'):
            dk_version = '[DEV]'
        return f'{name}@{dk_version}'
    return name


def _git_prompter(current_branch: str) -> str:
    branch = _branch_display(current_branch)
    status_res = git.get_status(check_stash=True)
    status, _ = status_res.get_or_else((UNKNOWN, UNKNOWN))
    status_color = STATUS_COLORS.get(status, UNKNOWN_COLOR)
    arrow = ''.join([r'\[', status_color, r'\]', '\u279C'])
    container_sec = COL(r'\[{green}\]', _container_info(), r'\[{white}\]:')
    branch_sec = _branch_sec(branch, status)
    repo, rel_path = _repo_info()
    repo_sec = COL(r'\[{blue}\]', repo)
    relpath_sec = COL(r'\[{gray}\]', rel_path)
    end = COL(r'\[{white}\]$')
    return f'{arrow} {container_sec}{repo_sec} {branch_sec} {relpath_sec}{end} '


def prompter() -> str:
    """Command line prompter.

    Returns:
        The string to be displayed in the prompt.
    """
    branch_res = git.get_branch()
    if isinstance(branch_res, Bad):
        return COL(r'\[{orange}\]\w\[{end}\]$ ')
    return _git_prompter(branch_res.value)
