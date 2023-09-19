from pydantic import BaseModel


class MEnvDocker(BaseModel):
    """Values from `MEnv` needed by docker."""

    # The m tag to build the images.
    m_tag: str

    # base path to locate docker file.
    base_path: str

    # docker registry
    registry: str
