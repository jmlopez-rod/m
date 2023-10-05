from textwrap import dedent
from typing import Callable, Generic, TypeVar, cast

from m.core import Good, Res, issue
from m.pydantic import KebabModel
from pydantic import BaseModel

from .misc import (
    ActionOutputs,
    InputOutputs,
    MetadataOutput,
    OutputField,
    get_inputs_outputs,
    input_env,
    map_args,
    verify_inputs,
)

InputModel = TypeVar('InputModel', bound=KebabModel)
OutputModel = TypeVar('OutputModel', bound=KebabModel)


class RunStep(BaseModel, Generic[InputModel, OutputModel]):
    """A "run" step in a Github action."""

    id: str

    run: Callable[[InputModel], Res[OutputModel]]

    args: InputModel | None

    def get_inputs_outputs(self: 'RunStep') -> InputOutputs:
        """Get the inputs and outputs for the step.

        Returns:
            A tuple of the inputs and outputs.
        """
        return get_inputs_outputs(self.run)

    def to_str(
        self: 'RunStep',
        python_path: str,
        available_values: dict[str, str],
    ) -> str:
        """Generate a string to use in the Github Action.

        Args:
            python_path: The path to the python module.
            available_values: The values that are available to the step.

        Returns:
            A string to add to the Github action.
        """
        template = """\
            - id: {id}
              shell: bash{env}
              run: PYTHONPATH="$GITHUB_ACTION_PATH{py_path}" python -m {mod}
        """
        # mypy has trouble seeing that its bound to KebabModel
        self_args = cast(KebabModel, self.args)
        all_args = self_args.model_dump() if self_args else {}
        mapped_args = map_args(all_args, available_values, input_env)
        env = ''
        if mapped_args:
            arg_lines = '\n'.join([
                f'    {key}: {env_val}'
                for key, env_val in mapped_args.items()
            ])
            env = f'\n  env:\n{arg_lines}'
        py_path = f'/{python_path}' if python_path else ''
        return dedent(template).format(
            id=self.id,
            env=env,
            py_path=py_path,
            mod=self.run.__module__,
        )


class UsesStep(BaseModel, Generic[InputModel, OutputModel]):
    """A "uses" step in a Github action."""

    id: str

    uses: str

    inputs: type[InputModel]

    outputs: type[OutputModel]

    args: InputModel | None

    def get_inputs_outputs(self: 'UsesStep') -> InputOutputs:
        """Get the inputs and outputs for the step.

        Returns:
            A tuple of the inputs and outputs.
        """
        return self.inputs, self.outputs

    def to_str(
        self: 'UsesStep',
        _python_path: str,
        available_values: dict[str, str],
    ) -> str:
        """Generate a string to use in the Github Action.

        Args:
            _python_path: The path to the python module.
            available_values: The values that are available to the step.

        Returns:
            A string to add to the Github action.
        """
        template = """\
            - id: {id}
              uses: {uses}{env}
        """
        # mypy has trouble seeing that its bound to KebabModel
        self_args = cast(KebabModel, self.args)
        all_args = self_args.model_dump() if self_args else {}
        mapped_args = map_args(
            all_args,
            available_values,
            lambda x: x.replace('_', '-', -1),
        )
        env = ''
        if mapped_args:
            arg_lines = '\n'.join([
                f'    {key}: {env_val}'
                for key, env_val in mapped_args.items()
            ])
            env = f'\n  with:\n{arg_lines}'
        return dedent(template).format(
            id=self.id,
            uses=self.uses,
            env=env,
        )


class Action(BaseModel):
    """A Github action."""

    file_path: str

    name: str

    description: str

    inputs: type[KebabModel] | None

    steps: list[RunStep | UsesStep]

    def gather_outputs(self: 'Action') -> Res[ActionOutputs]:
        """Obtain a tuple with the action outputs and all steps outputs.

        The steps outputs is a dictionary that maps keys of the form
        [step_id].[step_output_arg] to the output of another step, action
        input or some other value that should be used as input.

        This function validates that all the keys are valid.

        Returns:
            A tuple with the outputs if successful, otherwise an issue.
        """
        action_inputs = self.inputs or KebabModel
        available_outputs: dict[str, str] = {
            f'inputs.{name}': f'inputs.{arg_info.alias}'
            for name, arg_info in action_inputs.model_fields.items()
        }

        outputs: dict[str, MetadataOutput] = {}
        all_issues: dict[str, list[dict]] = {}
        for step in self.steps:
            input_model, output_model = step.get_inputs_outputs()
            output_fields = OutputField.create(step.id, output_model)
            # mypy has trouble seeing that its bound to KebabModel
            self_args = cast(KebabModel, step.args)
            all_args = self_args.model_dump() if self_args else {}
            issues = verify_inputs(input_model, all_args, available_outputs)
            if issues:
                all_issues[step.id] = [
                    iss.model_dump(exclude_none=True)
                    for iss in issues
                ]
            for name, field in output_fields.items():
                short_name = field.short_ref_name
                available_outputs[short_name] = field.full_ref_name
                if field.is_export:
                    outputs[name] = field.get_metadata_output()
        if all_issues:
            return issue('step_inputs_failure', context=all_issues)
        return Good((outputs, available_outputs))
