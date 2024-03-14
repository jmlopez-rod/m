from pydantic import BaseModel


class GithubWorkflowInput(BaseModel):
    """Declare extra workflow inputs."""

    type: str = 'string'
    description: str
    required: bool = True
