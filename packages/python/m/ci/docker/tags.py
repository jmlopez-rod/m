import re


def docker_tags(m_tag: str, *, skip_floating: bool = False) -> list[str]:
    """Convert an m_tag to docker tags.

    Floating tags include `latest` and any `vX` or `vX.Y` tags.
    The `skip_floating` argument is intended for use when building packages
    that have already been published in the past.

    Args:
        m_tag: A tag/version provided by m.
        skip_floating: If true, do not include floating tags.

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
        if not skip_floating:
            tags.append('latest')
            tags.append(f'v{x}')
            tags.append(f'v{x}.{y}')

    return tags
