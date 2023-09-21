import re


def docker_tags(m_tag: str) -> list[str]:
    """Convert an m_tag to docker tags.

    Args:
        m_tag: A tag/version provided by m.

    Returns:
        A tag that can be used by docker during the publishing step.
    """
    tags = []
    regex = r'\d+.\d+.\d+-(.*)\.(.*)'
    matches = re.match(regex, m_tag)
    if matches:
        tag, _ = matches.groups()
        if tag.startswith('rc') or tag.startswith('hotfix'):
            tags.append('next')
            index = 2 if tag.startswith('rc') else 6
            pr_num = tag[index:]
            tags.append(f'pr{pr_num}')
        else:
            tags.append(tag)
    else:
        x, y, _ = m_tag.split('.')
        tags.append('latest')
        tags.append(f'v{x}')
        tags.append(f'v{x}.{y}')

    return tags
