from re import sub

from pydantic import BaseModel


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

    class Config:
        """Config to allow camel case properties."""

        alias_generator = to_camel
        allow_population_by_field_name = True
