import re
from pathlib import Path
from textwrap import dedent
from typing import List, Tuple

from m.core import Good, Issue, OneOf, issue, one_of
from m.core import rw as mio
from m.core import subprocess
from m.git import get_remote_url
from m.log import Logger

logger = Logger('m.cli.init')


def parse_ssh_url(ssh_url: str) -> OneOf[Issue, Tuple[str, str]]:
    """Find the owner and repo from an ssh url.

    Args:
        ssh_url: The url of the repo

    Returns:
        A tuple with the owner and repo (or an Issue).
    """
    match = re.findall('.*:(.*)/(.*).git', ssh_url)
    if match and match[0] and match[0][0] and match[0][1]:
        return Good(match[0])
    return issue(
        'unable to obtain owner and repo',
        context={'ssh_url': ssh_url},
    )


def get_repo_info() -> OneOf[Issue, Tuple[str, str]]:
    """Get the owner and repo name from the current repository.

    Returns:
        A tuple with the owner and repo (or an Issue).
    """
    return one_of(lambda: [
        owner_repo
        for ssh_url in get_remote_url()
        for owner_repo in parse_ssh_url(ssh_url)
    ])


def m_json_body(owner: str, repo: str) -> str:
    """Create the basic contents of a m configuration file.

    Args:
        owner: The repo owner.
        repo: The repo name.

    Returns:
        A json string to be the content of the `m.json` file.
    """
    body = f"""\
        {{
          "owner": "{owner}",
          "repo": "{repo}",
          "version": "0.0.0",
          "workflow": "m_flow"
        }}
    """
    return dedent(body)


def create_m_config() -> OneOf[Issue, str]:
    """Create the m configuration file.

    Returns:
        A `OneOf` containing 0 if successful or an `Issue`.
    """
    m_dir = Path('m')
    if not Path.exists(m_dir):
        Path.mkdir(m_dir, parents=True)
    file_name = 'm/m.json'
    return one_of(lambda: [
        file_name
        for owner, repo in get_repo_info()
        for _ in mio.write_file(file_name, m_json_body(owner, repo))
        for _ in logger.info(f'created {file_name}', {
            'owner': owner,
            'repo': repo,
        })
    ])


def create_changelog() -> OneOf[Issue, str]:
    """Create the changelog file.

    Returns:
        A `OneOf` containing 0 if successful or an `Issue`.
    """
    body = """\
        # Changelog

        The format of this changelog is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/).
        The project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html)

        > Major version zero (0.y.z) is for initial development. Anything may change at any time.
        > The public API should not be considered stable.

        ## [Unreleased]
    """
    file_name = 'CHANGELOG.md'
    if Path.exists(Path(file_name)):
        logger.warning(f'{file_name} contents will be overwritten')
    return one_of(lambda: [
        file_name
        for _ in mio.write_file('CHANGELOG.md', dedent(body))
        for _ in logger.info(f'updated {file_name}')
    ])


def _update_gitignore(body: str) -> str:
    """List of things that should be in a gitignore file.

    Args:
        body: The current contents of the gitignore file.

    Returns:
        The contents of the new gitignore file.
    """
    buffer: List[str] = body.splitlines()
    if 'm/.m' not in body:
        buffer.append('m/.m')
    entries = '\n'.join(buffer)
    return f'{entries}\n'


def update_gitignore() -> OneOf[Issue, str]:
    """Update the gitignore file.

    Adds the m/.m directory to the list.

    Returns:
        A `OneOf` containing file name or an Issue if it was unable to update
        the file.
    """
    file_name = '.gitignore'
    return one_of(lambda: [
        file_name
        for _ in subprocess.eval_cmd(f'touch {file_name}')
        for body in mio.read_file(file_name)
        for _ in mio.write_file(file_name, _update_gitignore(body))
        for _ in logger.info(f'updated {file_name}')
    ])


def init_repo() -> OneOf[Issue, None]:
    """Initialize a repository with the basic project configurations.

    Returns:
        A `OneOf` containing 0 if successful or an `Issue`.
    """
    if Path.exists(Path('m/m.json')):
        logger.warning('delete m/m.json to restart the init process.')
        return Good(None)
    return one_of(lambda: [
        None
        for m_file in create_m_config()
        for gitignore in update_gitignore()
        for changelog in create_changelog()
        for _ in logger.info('setup complete', {
            'touched_files': [m_file, gitignore, changelog],
        })
    ])
