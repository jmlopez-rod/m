from pydantic import BaseModel


class MEnvDocker(BaseModel):
    """Values from `MEnv` needed by docker."""

    # The m tag to build the images.
    m_tag: str

    # base path to locate docker file.
    base_path: str

    # docker registry
    registry: str

    # pull request number, 0 if not a PR.
    pr_number: int

    # The pr number associated with the commit, 0 if there is none.
    associated_pr_number: int
