"""Generate the changelog page.

This will generate the `changelog.md` file from the `CHANGELOG.md` file. This
page should be manually added to the navigation section of the `mkdocs.yml`.

Each heading needs to be updated to include an anchor link.

https://www.markdownguide.org/extended-syntax/#heading-ids

The syntax is not compatible with Github markdown so we need to manually update
so that it looks good on our docs and in Github.
"""
import re
from pathlib import Path

import mkdocs_gen_files


def _modify_header(line: str) -> str:
    match = re.match(r'## \[(.*)] (.*)', line)
    if match:
        ver, date_link = match.groups()
        _, date = date_link.split('</a>')
        return f'## [{ver}] - {date} {{#{ver}}}'
    return line


def main():
    with open('../../CHANGELOG.md', 'r', encoding='utf-8') as chlog:
        changelog_content = chlog.read()
    new_changelog = [
        _modify_header(line)
        for line in changelog_content.splitlines()
    ]
    with mkdocs_gen_files.open(Path('changelog.md'), 'w') as fd:
        fd.write('\n'.join(new_changelog))


main()
