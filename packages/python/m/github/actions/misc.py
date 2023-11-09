import re
from inspect import signature
from typing import Callable

from m.core import Res
from m.pydantic import KebabModel
from pydantic import BaseModel
from pydantic.fields import FieldInfo

InputOutputs = tuple[type[KebabModel], type[KebabModel]]


class InputIssue(BaseModel):
    """An issue with an input."""

    # Set if the value is invalid, may be set of the form "input_name: value"
    invalid_input_value: str


class MetadataOutput(BaseModel):
    """An action metadata file output."""

    description: str
    value: str  # noqa: WPS110 - Actual name of property, cannot change.


def get_inputs_outputs(
    run_function: Callable[[KebabModel], Res[KebabModel]],
) -> InputOutputs:
    """Get the inputs and outputs of a `run_function`.

    Args:
        run_function: The function to obtain the inputs and outputs from.

    Returns:
        A tuple of the inputs and outputs.
    """
    func_sig = signature(run_function)
    in_params = func_sig.parameters
    arg_name = next(iter(in_params))
    input_model = in_params[arg_name].annotation
    out_sig = func_sig.return_annotation
    # expecting out_sig to be of type Res[Model] which is OneOf
    output_model: type[KebabModel] = out_sig.__args__[0].__args__[1]
    return input_model, output_model


def map_args(
    all_args: dict[str, str],
    available_values: dict[str, str],
    dict_key: Callable[[str], str],
) -> dict[str, str]:
    """Map the arguments to a new value using the available values.

    Args:
        all_args: A dictionary with mappable values.
        available_values: A dictionary with available values.
        dict_key: A transform function for the new key in the map.

    Returns:
        A mapped dictionary.
    """
    return {
        dict_key(key): (
            expression_eval(available_values[arg_val])
            if arg_val in available_values
            else arg_val
        )
        for key, arg_val in all_args.items()
    }


def is_input_key(key: str) -> bool:
    """Determine if a key is of the form `(step_id).(arg_name)`.

    Args:
        key: The key to check.

    Returns:
        True if the key is an input key.
    """
    pattern = r'^[\w-]+\.[\w-]+$'
    return bool(re.match(pattern, key))


def is_export(field: FieldInfo) -> bool:
    """Determine if a field is exported.

    Args:
        field: The field to check.

    Returns:
        Whether the field is exported.
    """
    if isinstance(field.json_schema_extra, dict):
        return bool(field.json_schema_extra.get('export', False))
    # internally we do not set json_schema_extra to something other than dict
    # If we are reaching the next step it is because of a custom field.
    return False  # pragma: no cover


def input_env(name: str) -> str:
    """Get the name of the env variable for an input.

    Args:
        name: The name of the input.

    Returns:
        The name of the env variable.
    """
    upper_name = name.replace('-', '_').upper()
    return f'INPUT_{upper_name}'


def expression_eval(gh_expression: str) -> str:
    """Create a string to evaluate a Github expression.

    Args:
        gh_expression: The Github expression to evaluate.

    Returns:
        A string to evaluate the Github expression.
    """
    left = '{{'
    right = '}}'
    return f'${left} {gh_expression} {right}'


def verify_inputs(
    input_model: type[KebabModel],
    args: dict[str, str],
    available_outputs: dict[str, str],
) -> list[InputIssue]:
    """Verify the inputs.

    This is used to make sure we declare valid arguments in each step
    along with valid accessible values from the global inputs or previous
    steps.

    Args:
        input_model: The model to use to verify the inputs.
        args: The arguments to verify.
        available_outputs: A dict of available outputs to use as inputs.

    Returns:
        A list of issues.
    """
    issues: list[InputIssue] = []
    for prop_name in input_model.model_fields:
        input_name = prop_name
        arg_value = args.get(input_name)
        not_available = arg_value not in available_outputs
        if arg_value and not_available and is_input_key(arg_value):
            issues.append(
                InputIssue(
                    invalid_input_value=f'{input_name}={arg_value}',
                ),
            )
    return issues


class OutputField(BaseModel):
    """Digestible information about an output."""

    # name of the output
    name: str

    # description of the output
    description: str

    # steps.{step_id}.outputs.{output_name}
    full_ref_name: str

    # {step_id}.{output_name}
    short_ref_name: str

    # flag to indicate if this output should be exported
    is_export: bool

    def get_metadata_output(self: 'OutputField') -> MetadataOutput:
        """Get the metadata output.

        Returns:
            An instance of the metadata output.
        """
        return MetadataOutput(
            description=self.description,
            value=expression_eval(self.full_ref_name),
        )

    @classmethod
    def create(
        cls: type['OutputField'],
        step_id: str,
        output_model: type[KebabModel],
    ) -> dict[str, 'OutputField']:
        """Create an instance of an output field.

        Args:
            step_id: The id of the step.
            output_model: The model to create it from.

        Returns:
            An instance of the output field.
        """
        outputs: dict[str, OutputField] = {}
        for name, prop_info in output_model.model_fields.items():
            kebab_name = prop_info.alias or name
            outputs[name] = OutputField(
                name=name,
                description=prop_info.description or '',
                full_ref_name=f'steps.{step_id}.outputs.{kebab_name}',
                short_ref_name=f'{step_id}.{name}',
                is_export=is_export(prop_info),
            )
        return outputs


# first item is the action outputs and second is the collection of all
# outputs that can be used when defining inputs in steps.
ActionOutputs = tuple[dict[str, MetadataOutput], dict[str, str]]
