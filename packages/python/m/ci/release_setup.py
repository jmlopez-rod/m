import re
from datetime import datetime

from m.ci.config import Config, get_m_filename, read_config
from m.core import Good, Issue, OneOf, issue, one_of, rw
from m.git import get_first_commit_sha
from m.github.ci import compare_sha_url
from m.log import Logger

logger = Logger('m.ci.release_setup')


def _get_versions(lines: list[str], new_ver: str, first_sha: str) -> list[str]:
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
    changelog_contents: str,
    owner: str,
    repo: str,
    new_ver: str,
    first_sha: str,
) -> OneOf[Issue, str]:
    """Modify the contents of a CHANGELOG.

    It adds a new entry with the new version the new changelog contents.

    Args:
        changelog_contents: The current contents of the CHANGELOG file.
        owner: The repo owner.
        repo: The repo name.
        new_ver: The new version.
        first_sha: The very first commit sha of the repo.

    Returns:
        The new contents of the CHANGELOG.
    """
    parts = changelog_contents.split('## [Unreleased]')
    if len(parts) != 2:
        return issue('missing "Unreleased" link')

    header, main = parts
    entries = main.split('[unreleased]:')[0]
    versions = _get_versions(entries.split('\n'), new_ver, first_sha)

    compare_url = compare_sha_url(owner, repo, new_ver, 'HEAD')
    links = [f'[unreleased]: {compare_url}']
    for i in range(len(versions) - 1):
        link = compare_sha_url(owner, repo, versions[i + 1], versions[i])
        links.append(f'[{versions[i]}]: {link}')

    date = datetime.now().strftime('%B %d, %Y')
    ver_anchor = _version_anchor(new_ver)
    return Good(''.join([
        header,
        '## [Unreleased]\n\n',
        f'## [{new_ver}] {ver_anchor} {date}\n\n',
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
        first_sha: The first sha ever committed on the repo.
        filename: Specify the CHANGELOG file (defaults to CHANGELOG.md)

    Returns:
        0 if successful, an issue otherwise.
    """
    return one_of(lambda: [
        0
        for text in rw.read_file(filename)
        for new_data in new_changelog(text, owner, repo, new_ver, first_sha)
        for _ in rw.write_file(filename, new_data)
        for _ in logger.info(f'updated {filename}')
    ])


def _update_line_version(line: str, ver: str) -> str:
    stripped_line = line.strip()
    if stripped_line.startswith('"version"'):
        comma = ',' if stripped_line.endswith(',') else ''
        return f'  "version": "{ver}"{comma}'
    if stripped_line.startswith('version'):
        return f'version: {ver}'
    return line


def _update_config_version(
    config_contents: str,
    ver: str,
) -> OneOf[Issue, str]:
    lines = config_contents.split('\n')
    new_lines = [_update_line_version(line, ver) for line in lines]
    return Good('\n'.join(new_lines))


def update_version(
    root: str,
    version: str,
) -> OneOf[Issue, int]:
    """Update the version property in m configuration file.

    Args:
        root: The directory with the m configuration file.
        version: The new version to write in the m configuration.

    Returns:
        0 if successful or an issue.
    """
    return one_of(lambda: [
        0
        for filename in get_m_filename(root)
        for config_contents in rw.read_file(filename)
        for new_data in _update_config_version(config_contents, version)
        for _ in rw.write_file(filename, new_data)
        for _ in logger.info(f'bumped version in {filename}')
    ])


def _success_release_setup(config: Config, new_ver: str) -> OneOf[Issue, int]:
    link = compare_sha_url(config.owner, config.repo, config.version, 'HEAD')
    return logger.info('setup complete', {
        'new_version': new_ver,
        'unreleased_changes': link,
    })


def _read_config(m_dir: str, config: Config | None) -> OneOf[Issue, Config]:
    if config:
        return Good(config)
    return read_config(m_dir)


def release_setup(
    m_dir: str,
    config_inst: Config | None,
    new_ver: str,
    changelog: str = 'CHANGELOG.md',
) -> OneOf[Issue, None]:
    """Modify all the necessary files to create a release.

    These include: CHANGELOG.md and the m configuration file.

    Args:
        m_dir: The directory with the m configuration.
        config_inst: If provided it skips reading the configuration.
        new_ver: The new version to write in the m configuration.
        changelog: The name of the changelog file (defaults to CHANGELOG.md)

    Returns:
        None if successful, otherwise an issue.
    """
    return one_of(lambda: [
        None
        for config in _read_config(m_dir, config_inst)
        for first_sha in get_first_commit_sha()
        for _ in update_version(m_dir, new_ver)
        for _ in update_changelog_file(
            config.owner,
            config.repo,
            new_ver,
            first_sha,
            changelog,
        )
        for _ in _success_release_setup(config, new_ver)
    ])
