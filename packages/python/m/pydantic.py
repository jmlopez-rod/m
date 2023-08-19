from re import sub

from pydantic import BaseModel, ConfigDict


def to_camel(snake_case: str) -> str:
    """Transform a string in snake_case to camel case.

    Args:
        snake_case: string in snake case.

    Returns:
        string in camel case.
    """
    s = sub('(_|-)+', ' ', snake_case).title().replace(' ', '')
    return ''.join([s[0].lower(), s[1:]])


class CamelModel(BaseModel):
    """Allows models to be defined with camel case properties.

    See:
        https://medium.com/analytics-vidhya/camel-case-models-with-fast-api-and-pydantic-5a8acb6c0eee
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )
