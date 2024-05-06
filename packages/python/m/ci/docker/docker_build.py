from pydantic import BaseModel

from .shell_command import ShellCommand


class DockerBuild(BaseModel):
    """Representation of a `docker build` command.

    See https://docs.docker.com/engine/reference/commandline/build
    """

    # Add a custom host-to-IP mapping (host:ip)
    add_host: list[str] | None = None

    # Set build-time variables
    build_arg: list[str] | None = None

    # Images to consider as cache sources
    cache_from: str | None = None

    # Optional parent cgroup for the container
    cgroup_parent: str | None = None

    # Compress the build context using gzip
    compress: bool | None = None

    # Limit the CPU CFS (Completely Fair Scheduler) period
    cpu_period: int | None = None

    # Limit the CPU CFS (Completely Fair Scheduler) quota
    cpu_quota: int | None = None

    # CPU shares (relative weight)
    cpu_shares: int | None = None

    # CPUs in which to allow execution (0-3, 0,1)
    cpuset_cpus: str | None = None

    # MEMs in which to allow execution (0-3, 0,1)
    cpuset_mems: str | None = None

    # Skip image verification (default true)
    disable_content_trust: bool | None = None

    # Name of the Dockerfile (Default is 'PATH/Dockerfile')
    file: str | None = None  # noqa: WPS110 - docker build optional argument

    # Always remove intermediate containers
    force_rm: bool | None = None

    # Write the image ID to the file
    iidfile: str | None = None

    # Container isolation technology
    isolation: str | None = None

    # Set metadata for an image
    label: list[str] | None = None

    # Memory limit
    memory: str | None = None

    # Swap limit equal to memory plus swap: '-1' to enable unlimited swap
    memory_swap: str | None = None

    # Set the networking mode for the RUN instructions during build (default "default")
    network: str | None = None

    # Do not use cache when building the image
    no_cache: bool | None = None

    # Always attempt to pull a newer version of the image
    pull: bool | None = None

    # Suppress the build output and print image ID on success
    quiet: bool | None = None

    # Remove intermediate containers after a successful build (default true)
    rm: bool | None = None

    # Security options
    security_opt: str | None = None

    # Available with DOCKER_BUILDKIT=1
    #   see https://pythonspeed.com/articles/docker-build-secrets
    # Use as `--secret id=ENVVAR` in the docker build command.
    # Then in the `RUN` statement in the docker file do `RUN --mount=type=secret,id=ENVVAR`.
    # Then you may access that value by doing `ENVVAR=$(cat /run/secrets/ENVVAR)`.
    # Best to use that in a script that that executes inside the docker file.
    secret: list[str] | None = None

    # Available with DOCKER_BUILDKIT=1
    progress: str | None = None

    # Size of /dev/shm
    shm_size: str | None = None

    # Name and optionally a tag in the 'name:tag' format
    tag: list[str] | None = None

    # Set the target build stage to build
    target: str | None = None

    # Ulimit options (default [])
    ulimit: str | None = None

    def __str__(self) -> str:
        """Convert the docker build command to a string.

        Returns:
            The docker build command.
        """
        cmd = ShellCommand(
            prog='docker build',
            positional=['.'],
            options=self.model_dump(exclude_none=True),
        )
        return str(cmd)

    def buildx_str(self) -> str:
        """Convert the docker build command to a string.

        Returns:
            The docker build command.
        """
        cmd = ShellCommand(
            prog='docker buildx build --platform "$PLATFORM"',
            positional=['.'],
            options=self.model_dump(exclude_none=True),
        )
        return str(cmd)
