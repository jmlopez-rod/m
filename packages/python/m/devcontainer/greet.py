from m.log import Logger


def greet(img_name: str, img_version: str, changelog_url: str | None) -> None:
    """Log an "info" message to the console stating that the container is ready.

    Args:
        img_name: The name of the image.
        img_version: The version of the image.
        changelog_url: The URL to the changelog.
    """
    logger = Logger(__name__)
    context = {
        'name': img_name,
        'version': img_version,
        'TIP': 'set `DEBUG`/`DEBUG_M_LOGS` to true to display debugging info',
    }
    if not img_version.startswith('0.0.0') and changelog_url:
        context['changelog'] = f'{changelog_url}#{img_version}'
    logger.info('container_ready', context=context)
