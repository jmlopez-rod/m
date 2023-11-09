from re import sub
from typing import Any, Callable, TypeVar

from pydantic import BaseModel, ConfigDict, TypeAdapter

from .core import Good, Res, hone, issue, one_of
from .core.rw import assert_file_exists
from .core.yaml_fp import read_yson

GenericModel = TypeVar('GenericModel')


def to_camel(snake_case: str) -> str:
    """Transform a string in snake_case to camel case.

    Args:
        snake_case: string in snake case.

    Returns:
        string in camel case.
    """
    s = sub('(_|-)+', ' ', snake_case).title().replace(' ', '')
    return ''.join([s[0].lower(), s[1:]])


def to_kebab(snake_case: str) -> str:
    """Transform a string in snake_case to kebab case.

    Args:
        snake_case: string in snake case.

    Returns:
        string in kebab case.
    """
    return snake_case.replace('_', '-', -1)


class CamelModel(BaseModel):
    """Allows models to be defined with camel case properties.

    See:
        https://medium.com/analytics-vidhya/camel-case-models-with-fast-api-and-pydantic-5a8acb6c0eee
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


class KebabModel(BaseModel):
    """Allows models to be defined with kebab case properties.

    Inputs and outputs need to be written using a `KebabModel` as a base class.
    This is so that their definitions may be written using kebab casing in the
    final `action.yaml`.

    ```python
    from m.github.actions import KebabModel, InArg

    class MyInput(KebabModel):
        my_input: str = InArg(help='description')
    ```
    """

    model_config = ConfigDict(
        alias_generator=to_kebab,
        populate_by_name=True,
    )


def parse_model(model: type[GenericModel], model_data: Any) -> Res[GenericModel]:
    """Parse a python object using pydantics TypeAdapter.

    Args:
        model: The class to create an instance of.
        model_data: The data to parse.

    Returns:
        A `OneOf` with the model or an issue.
    """
    try:
        return Good(TypeAdapter(model).validate_python(model_data))
    except Exception as ex:
        return issue('parse_model_failure', cause=ex)


DataTransformer = Callable[[Any], Res[Any]]


def load_model(
    model: type[GenericModel],
    file_path: str,
    transform: DataTransformer | None = None,
) -> Res[GenericModel]:
    """Load a model from a json or yaml file.

    Args:
        model: The class to create an instance of.
        file_path: The path to the file.
        transform: A function to transform the data before creating the model.

    Returns:
        A `OneOf` with the model or an issue.
    """
    context = {'file_path': file_path, 'model': str(model)}
    transform_function = transform or Good
    return one_of(
        lambda: [
            model_inst
            for _ in assert_file_exists(file_path)
            for model_data in read_yson(file_path)
            for transformed_data in transform_function(model_data)
            for model_inst in parse_model(model, transformed_data)
        ],
    ).flat_map_bad(hone('pydantic.load_model_failure', context))
