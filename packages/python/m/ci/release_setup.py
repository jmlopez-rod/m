import re
from datetime import datetime
from typing import List
from ..core.io import read_file, write_file
from ..core.fp import OneOf, Good, one_of
from ..core.issue import Issue, issue
from ..github import compare_sha_url


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
    first_sha: str
) -> OneOf[Issue, str]:
    """Modify the contents of a CHANGELOG so that a new entry with the new
    version is added to the new changelog contents."""
    parts = content.split('## [Unreleased]')
    if len(parts) != 2:
        return issue('missing "Unreleased" link')

    header, main = parts
    entries = main.split('[Unreleased]:')[0]
    versions = _get_versions(entries.split('\n'), new_ver, first_sha)

    links = [f'[Unreleased]: {compare_sha_url(owner, repo, new_ver, "HEAD")}']
    for i in range(len(versions) - 1):
        link = compare_sha_url(owner, repo, versions[i+1], versions[i])
        links.append(f'[{versions[i]}]: {link}')

    date = datetime.now().strftime('%B %d, %y')
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
    """Add an entry to the CHANGELOG file with the new version to be released.
    """
    return one_of(lambda: [
        0
        for data in read_file(filename)
        for new_data in new_changelog(data, owner, repo, new_ver, first_sha)
        for _ in write_file(filename, new_data)
    ])
