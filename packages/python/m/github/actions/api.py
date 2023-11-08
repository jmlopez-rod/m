import os
import sys
from collections.abc import Callable
from inspect import signature
from typing import Any, TypeVar

from m.cli import run_main
from m.cli.cli import default_issue_handler
from m.core import Bad, Good, Issue, Res, issue, rw
from m.log import logging_config
from m.pydantic import KebabModel
from pydantic import TypeAdapter
from pydantic.fields import FieldInfo

InputModel = TypeVar('InputModel', bound=KebabModel)
OutputModel = TypeVar('OutputModel', bound=KebabModel)


def load_step_inputs(model: type[InputModel]) -> Res[InputModel]:
    """Load the GitHub Action inputs from the environment.

    This function can be used provided that in the GitHub Action workflow we
    set up:::

        env:
            INPUT_ARG_1: ${{ inputs.arg-1 }}

    In this way the inputs will set in the environment which we can then read
    in our main python function.

    Args:
        model: The class to create an instance of.

    Returns:
        A `OneOf` with the model or an issue.
    """
    model_data: dict[str, str] = {}
    for key, env_val in os.environ.items():
        if key.startswith('INPUT_'):
            _, input_name = key.split('INPUT_')
            model_data[input_name.lower()] = env_val
    try:
        return Good(TypeAdapter(model).validate_python(model_data))
    except Exception as ex:
        return issue('load_step_inputs_failure', cause=ex)


def dump_step_outputs(outputs: OutputModel) -> Res[int]:
    """Dump the outputs for a GitHub Action step.

    Github does this if we write to the file where $GITHUB_OUTPUT is pointing.

    Args:
        outputs: The outputs to dump.

    Returns:
        A `OneOf` with 0 or an issue.
    """
    output_data = '\n'.join([
        f'{key}={output_val}'
        for key, output_val in outputs.model_dump(by_alias=True).items()
    ])
    output_file = os.environ.get('GITHUB_OUTPUT', 'NO_GITHUB_OUTPUT_FILE')
    return rw.write_file(output_file, output_data, 'a')


def _result_handler(outputs: OutputModel) -> None:
    try:
        res = dump_step_outputs(outputs)
    except Exception as ex:
        default_issue_handler(Issue('dump_step_outputs', cause=ex))
        sys.exit(5)
    if isinstance(res, Bad):
        default_issue_handler(res.value)
        sys.exit(6)


def run_action(main: Callable[[InputModel], Res[OutputModel]]) -> None:
    """Entry point for a GitHub Action.

    This is the main function that should be used to run an action. It takes in
    a function that takes in a [m.pydantic.KebabModel][] and returns a
    `Res[KebabModel]`.

    The only place where this function is needed is in the the if block

    ```python
    if __name__ == '__main__':
        run_action(my_action)
    ```

    `mypy` will make sure that the you are providing the correct type of function
    to `run_action`. Keep in mind, the function is generic and we should be writing
    models for the inputs and outputs for all of our functions.

    Args:
        main: The main function of the GitHub Action.
    """
    logging_config()
    main_params = signature(main).parameters
    arg_name = next(iter(main_params))
    input_model = main_params[arg_name].annotation
    args = load_step_inputs(input_model)
    if isinstance(args, Bad):
        default_issue_handler(args.value)
        sys.exit(4)
    inputs = args.value
    exit_code = run_main(lambda: main(inputs), result_handler=_result_handler)
    sys.exit(exit_code)


def InArg(  # noqa: N802
    *,
    help: str,  # noqa: WPS125
    default: str | None = None,
) -> Any:
    """Force proper annotation of the input of a GitHub Action.

    Should be used to declare the input arguments of an action. It returns
    [`Any`][typing.Any] to bypass `mypy`'s type checking. Similar to
    [pydantic.fields.Field][] but it is tailored to help us write the inputs for
    an action and its steps.

    !!! note

        By default all input arguments are required. If you want to make an
        input not required then provide a default value.

    Args:
        help: Human-readable description.
        default: The default value for the argument.

    Returns:
        A new [`FieldInfo`][pydantic.fields.FieldInfo], the return annotation is
            `Any` so `InArg` can be used on type annotated fields without
            causing typing errors.
    """
    args = {
        'description': help,
    }
    if default is not None:
        args['default'] = default
    return FieldInfo.from_field(**args)


def OutArg(  # noqa: N802
    *,
    help: str,  # noqa: WPS125
    export: bool = False,
) -> Any:
    """Force proper annotation of the output of a GitHub Action.

    !!! note
        All steps have access to the steps output, if we want to make the output
        available to the action we need to `export` it.

    Args:
        help: Human-readable description.
        export: Whether the argument is to be exported to the action.

    Returns:
        A new [`FieldInfo`][pydantic.fields.FieldInfo], the return annotation is
            `Any` so `Arg` can be used on type annotated fields without causing
            a typing error.
    """
    return FieldInfo.from_field(
        description=help,
        json_schema_extra={'export': export},
    )
