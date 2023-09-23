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
