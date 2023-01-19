import re
from datetime import datetime
from typing import List

from m.ci.config import Config, read_config
from m.core import issue, one_of
from m.core.fp import Good, OneOf
from m.core.issue import Issue
from m.core import rw
from m.git import get_first_commit_sha
from m.github import compare_sha_url


def _get_versions(lines: List[str], new_ver: str, first_sha: str) -> List[str]:
    versions = [new_ver]
    for line in lines:
        match = re.match(r'## \[(.*)]', line)
        if match:
            versions.append(match.groups()[0])
    versions.append(first_sha)
    return versions


def _version_anchor(ver: str) -> str:
    return f'<a name="{ver}" href="#{ver}">-</a>'


def new_changelog(
    content: str,
    owner: str,
    repo: str,
    new_ver: str,
    first_sha: str,
) -> OneOf[Issue, str]:
    """Modify the contents of a CHANGELOG so that a new entry with the new
    version is added to the new changelog contents."""
    parts = content.split('## [Unreleased]')
    if len(parts) != 2:
        return issue('missing "Unreleased" link')

    header, main = parts
    entries = main.split('[unreleased]:')[0]
    versions = _get_versions(entries.split('\n'), new_ver, first_sha)

    links = [f'[unreleased]: {compare_sha_url(owner, repo, new_ver, "HEAD")}']
    for i in range(len(versions) - 1):
        link = compare_sha_url(owner, repo, versions[i + 1], versions[i])
        links.append(f'[{versions[i]}]: {link}')

    date = datetime.now().strftime('%B %d, %Y')
    return Good(''.join([
        header,
        '## [Unreleased]\n\n',
        f'## [{new_ver}] {_version_anchor(new_ver)} {date}\n\n',
        entries,
        '\n'.join(links),
        '\n',
    ]))


def update_changelog_file(
    owner: str,
    repo: str,
    new_ver: str,
    first_sha: str,
    filename: str = 'CHANGELOG.md',
) -> OneOf[Issue, int]:
    """Add the new version entry to be released to the CHANGELOG.

    Args:
        owner: The repo owner.
        repo: The repo name.
        new_ver: The version that is being released.
        first_sha: The first sha ever commited on the repo.
        filename: Specify the CHANGELOG file (defaults to CHANGELOG.md)

    Returns:
        0 if successful, an issue otherwise.
    """
    return one_of(lambda: [
        0
        for text in rw.read_file(filename)
        for new_data in new_changelog(text, owner, repo, new_ver, first_sha)
        for _ in rw.write_file(filename, new_data)
    ])


def _update_line_version(line: str, ver: str) -> str:
    content = line.strip()
    if not content.startswith('"version"'):
        return line
    comma = ',' if content.endswith(',') else ''
    return f'  "version": "{ver}"{comma}'


def _update_config_version(contents: str, ver: str) -> OneOf[Issue, str]:
    lines = contents.split('\n')
    new_lines = [_update_line_version(line, ver) for line in lines]
    return Good('\n'.join(new_lines))


def update_version(
    root: str,
    version: str,
    m_file: str,
) -> OneOf[Issue, int]:
    """Update the version property in m configuration file.

    Args:
        root: The directory with the m configuration file.
        version: The new version to write in the m configuration.
        m_file: Specify either `m.json` or `m.yaml`.

    Returns:
        0 if successful or an issue.
    """
    filename = f'{root}/{m_file}'
    return one_of(lambda: [
        0
        for data in rw.read_file(filename)
        for new_data in _update_config_version(data, version)
        for _ in rw.write_file(filename, new_data)
    ])


def _success_release_setup(config: Config, new_ver: str) -> OneOf[Issue, int]:
    link = compare_sha_url(config.owner, config.repo, config.version, 'HEAD')
    print(f'\nSetup for version {new_ver} is complete.')
    print(f'Unreleased changes: {link}\n')
    print('what')
    return Good(0)


def release_setup(
    m_dir: str,
    new_ver: str,
    m_file: str,
    changelog: str = 'CHANGELOG.md',
) -> OneOf[Issue, None]:
    """Modify all the necessary files to create a release.

    These include: CHANGELOG.md and the m configuration file.

    Args:
        m_dir: The directory with the m configuration.
        new_ver: The new version to write in the m configuration.
        m_file: The name of the m configuration file (m.json, m.yaml).
        changelog: The name of the changelog file (defaults to CHANGELOG.md)

    Returns:
        None if successul, otherwise an issue.
    """
    return one_of(lambda: [
        None
        for config in read_config(m_dir)
        for first_sha in get_first_commit_sha()
        for _ in update_version(m_dir, new_ver, m_file)
        for _ in update_changelog_file(
            config.owner,
            config.repo,
            new_ver,
            first_sha,
            changelog)
        for _ in _success_release_setup(config, new_ver)
    ])
