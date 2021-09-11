import inspect
import os
import re
from pathlib import Path
from typing import List, Tuple

from ..core import issue, one_of
from ..core.fp import Good, OneOf
from ..core.io import CiTool, read_file, write_file
from ..core.issue import Issue
from ..core.subprocess import eval_cmd
from ..git import get_remote_url


def parse_ssh_url(ssh_url: str) -> OneOf[Issue, Tuple[str, str]]:
    """Find the owner and repo from an ssh url."""
    match = re.findall('.*:(.*)/(.*).git', ssh_url)
    if match:
        return Good(match[0])
    return issue('unable to obtain owner and repo', data=dict(ssh_url=ssh_url))


def get_repo_info() -> OneOf[Issue, Tuple[str, str]]:
    """Get the owner and repo name from the current repository."""
    return one_of(lambda: [
        info
        for ssh_url in get_remote_url()
        for info in parse_ssh_url(ssh_url)
    ])


def m_json_body(owner: str, repo: str) -> str:
    """Create the basic contents of a m configuration file."""
    return inspect.cleandoc(f'''
        {{
          "owner": "{owner}",
          "repo": "{repo}",
          "version": "0.0.0"
        }}
    ''') + '\n'


def _changelog_body() -> str:
    return inspect.cleandoc('''
        # Changelog

        The format of this changelog is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).
        The project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html)

        > Major version zero (0.y.z) is for initial development. Anything may change at any time.
        > The public API should not be considered stable.

        ## [Unreleased]
    ''') + '\n'  # noqa


def create_m_config() -> OneOf[Issue, int]:
    """Create the m configuration file."""
    if not os.path.exists('m'):
        os.makedirs('m')
    return one_of(lambda: [
        0
        for owner, repo in get_repo_info()
        for _ in write_file('m/m.json', m_json_body(owner, repo))
    ])


def create_changelog() -> OneOf[Issue, int]:
    """Create the changelog file."""
    return write_file('CHANGELOG.md', _changelog_body())


def _update_gitignore(body: str) -> str:
    """List of things that should be in a gitignore file."""
    buffer: List[str] = []
    if 'm/.m' not in body:
        buffer.append('m/.m')
    return body + '\n'.join(buffer) + '\n'


def update_gitignore() -> OneOf[Issue, int]:
    """Updates the gitignore file."""
    return one_of(lambda: [
        0
        for _ in eval_cmd('touch .gitignore')
        for body in read_file('.gitignore')
        for _ in write_file('.gitignore', _update_gitignore(body))
    ])


def init_repo() -> OneOf[Issue, int]:
    """Initialize a repository with the basic project configurations."""
    obra_path = Path('m/m.json').resolve()
    if obra_path.exists():
        CiTool.warn('delete m/m.json to restart the init process.')
        return Good(0)
    return one_of(lambda: [
        0
        for _ in create_m_config()
        for _ in update_gitignore()
        for _ in create_changelog()
    ])
