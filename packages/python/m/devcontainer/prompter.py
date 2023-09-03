from pathlib import Path

from m.color.colors import color
from m.core import Bad, subprocess

from m import git

UNKNOWN_COLOR = '\033[38;5;20m'
STATUS_SYMBOLS = {
    'unknown': '???',
    'untracked': '?',
    'stash': '+',
    'ahead': '>',
    'behind': '<',
    'clean': '✔',
    'staged': '●',
    'dirty': '✖',
    'diverged': '!',
}
STATUS_COLORS = {
    'unknown': UNKNOWN_COLOR,  # dark blue
    'untracked': '\033[38;5;76m',  # mid lime-green
    'stash': '\033[38;5;76m',  # mid lime-green
    'ahead': '\033[38;5;226m',  # bright yellow
    'behind': '\033[38;5;142m',  # darker yellow-orange
    'clean': '\033[38;5;82m',  # brighter green
    'staged': '\033[38;5;214m',  # orangey yellow
    'dirty': '\033[38;5;202m',  # orange
    'diverged': '\033[38;5;196m',  # red
}

def _branch_display(current_branch: str) -> str:
    # if the branch is HEAD, display the commit hash instead
    if current_branch == 'HEAD':
        short_res = subprocess.eval_cmd('git rev-parse --short HEAD')
        return short_res.get_or_else(current_branch)
    return current_branch


def _branch_sec(branch: str, status: str) -> str:
    s_color = STATUS_COLORS.get(status, UNKNOWN_COLOR)
    s_sym = STATUS_SYMBOLS.get(status, '???')
    branch_info = color(s_color, branch, '{bold}', s_color, s_sym)
    return color('{gray}[', branch_info, '{gray}]')

def _repo_info() -> tuple[str, str]:
    repo_path = git.get_repo_path().get_or_else('[UNKNOWN_REPO_PATH]')
    cwd =  str(Path.cwd())
    repo = repo_path.split('/')[-1]
    rel_path = cwd.replace(repo_path, '^', 1)
    return repo, rel_path

def _git_prompter(current_branch: str) -> str:
    branch = _branch_display(current_branch)
    status, _ = git.get_status().get_or_else(('unknown', 'unknown'))
    status_color = STATUS_COLORS.get(status, UNKNOWN_COLOR)
    arrow = f'{status_color}\\342\\236\\234'
    container_sec = color('{green}', 'container', '{white}:')
    branch_sec = _branch_sec(branch, status)
    repo, rel_path = _repo_info()
    repo_sec = color('{blue}', repo)
    relpath_sec = color('{gray}', rel_path)
    end = color('{white}$')
    return f'{arrow} {container_sec}{repo_sec} {branch_sec} {relpath_sec}{end} '


def prompter() -> str:
    """Command line prompter.

    Returns:
        The string to be displayed in the prompt.
    """
    branch_res = git.get_branch()
    if isinstance(branch_res, Bad):
        return color('{orange}\\w{end}$ ')
    return _git_prompter(branch_res.value)
