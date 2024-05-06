from pydantic import BaseModel


class MEnvDocker(BaseModel):
    """Values from `MEnv` needed by docker."""

    # The m tag to build the images.
    m_tag: str

    # The pull request number to attempt to use as cache.
    cache_from_pr: str

    # base path to locate docker file.
    base_path: str

    # docker registry
    registry: str

    # Flag to indicate if multi-arch is enabled.
    multi_arch: bool

    # The list of all the architectures if multi-arch is enabled.
    architectures: list[str]

    # Flag to indicate if buildx should be used.
    use_buildx: bool = False
