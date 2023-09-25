import os

from m.log import Logger

from .tags import docker_tags

logger = Logger('m.ci.docker.shell_scripts')

FIND_CACHE_SCRIPT = """\
#!/bin/bash
imageName=$1
pullCache() {{
  if docker pull -q "$1:$2" 2> /dev/null; then
    docker tag "$1:$2" "staged-image:cache"
  else
    return 1
  fi
}}
findCache() {{
  {find_cache_implementation}
}}
set -euxo pipefail
findCache "{docker_registry}/$imageName"
"""

PUSH_SCRIPT = """\
#!/bin/bash
imageName=$1
set -euxo pipefail
docker tag staged-image:latest "{docker_registry}/$ARCH-$imageName:$M_TAG"
docker push "{docker_registry}/$ARCH-$imageName:$M_TAG"
"""

PUSH_SCRIPT_TAGS = """\
#!/bin/bash
imageName=$1
set -euxo pipefail
{tag_images}
docker image push --all-tags "{docker_registry}/$imageName"
"""


def create_cache_script(pr_num: str, docker_registry: str) -> str:
    """Create a script to retrieve cache for an image.

    Args:
        pr_num: The pull request number where to pull the cache from.
        docker_registry: The docker registry where the images are located.

    Returns:
        A script to find the cache.
    """
    pulls = ['pullCache "$1" master', 'echo "NO CACHE FOUND"']
    if pr_num:
        pulls.insert(0, f'pullCache "$1" "pr{pr_num}"')
    find_cache_implementation = ' || '.join(pulls)
    replacements = {
        'docker_registry': docker_registry,
        'find_cache_implementation': find_cache_implementation,
    }
    return FIND_CACHE_SCRIPT.format(**replacements)


def create_push_script(docker_registry: str) -> str:
    """Create a script to push an image.

    Args:
        docker_registry: The docker registry where the images will be pushed.

    Returns:
        A script to push an image.
    """
    return PUSH_SCRIPT.format(docker_registry=docker_registry)


def create_push_script_tags(docker_registry: str, m_tag: str) -> str:
    """Create a script to push an image.

    This is meant to be used when building for a single architecture.

    Args:
        docker_registry: The docker registry where the images will be pushed.
        m_tag: The unique tag for the image.

    Returns:
        A script to push an image.
    """
    if not m_tag and os.environ.get('CI') != 'true':
        logger.warning('M_TAG not found in non-CI environment. Using 1.1.1')
        m_tag = '1.1.1'
    tags = [m_tag, *docker_tags(m_tag)]
    tagged_images = '\n'.join([
        f'docker tag staged-image:latest "{docker_registry}/$imageName:{tag}"'
        for tag in tags
    ])
    return PUSH_SCRIPT_TAGS.format(
        docker_registry=docker_registry,
        tag_images=tagged_images,
    )
