import re


def npm_tags(m_tag: str) -> list[str]:
    """Convert an m_tag to an npm_tag.

    Args:
        m_tag: A tag/version provided by m.

    Returns:
        A tag that can be used by npm during the publishing step.
    """
    tags = []
    regex = r'\d+.\d+.\d+-(.*)\.(.*)'
    matches = re.match(regex, m_tag)
    if matches:
        tag, _ = matches.groups()
        if tag.startswith('rc') or tag.startswith('hotfix'):
            tags.append('next')
        else:
            tags.append(tag)
    else:
        tags.append('latest')
    return tags
