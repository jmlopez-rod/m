from typing import Any

from pydantic import BaseModel, ConfigDict


def to_kebab(snake: str) -> str:
    """Convert a PascalCase or camelCase string to snake_case.

    Args:
        camel: The string to convert.

    Returns:
        The converted string in snake_case.
    """
    return snake.replace('_', '-', -1)

class Job(BaseModel):
    """Representation of a Github job."""

    model_config = ConfigDict(alias_generator=to_kebab, extra='allow')

    runs_on: str | list[str]

    steps: list[dict[str, Any]]


class Workflow(BaseModel):
    """"Representation of a Github workflow."""

    model_config = ConfigDict(alias_generator=to_kebab, extra='allow')

    name: str

    jobs: dict[str, Job]

    on: dict[str, Any]
