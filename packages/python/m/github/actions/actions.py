import re
from functools import partial
from textwrap import dedent
from typing import Callable, Generic, TypeVar, cast

from m.core import Good, Res, issue
from m.log import Logger
from m.pydantic import KebabModel
from pydantic import BaseModel
from pydantic.fields import Field

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
logger = Logger('m.github.actions')


def _replace_values(available_values: dict[str, str], match: re.Match) -> str:
    step_id, arg_name = match.groups()
    key = f'{step_id}.{arg_name}'
    if key not in available_values:
        logger.warning(f'Unknown step value: {key}')
    return available_values.get(key, key)


def _run_if(condition: str | None, available_values: dict[str, str]) -> str:
    run_if = ''
    if condition:
        replace = partial(_replace_values, available_values)
        with_replacements = re.sub(
            r'\$([\w-]+).([\w-]+)',
            replace,
            condition,
            flags=re.I | re.M,
        )
        run_if = f'\n  if: {with_replacements}'
    return run_if


class BashStep(BaseModel, Generic[InputModel, OutputModel]):
    """Step to add bash scripting into the action.

    This step does not connect to any of the others one and its been added
    to be able to run poetry commands or any other setup that we may need in
    the action.
    """

    id: str = Field(description='The id of the step.')

    run_if: str | None = Field(
        default=None,
        description='The condition to run the step.',
    )

    run: str = Field(
        description='The bash script to execute.',
    )

    args: InputModel | None = Field(
        default=None,
        description='The arguments to pass to the run function.',
    )

    def get_inputs_outputs(self: 'BashStep') -> InputOutputs:
        """Get the inputs and outputs for the step.

        Returns:
            A tuple of the inputs and outputs.
        """
        return KebabModel, KebabModel


    def _sanitize_run(self: 'BashStep') -> str:
        spaces = '  ' * 2
        return dedent(self.run).replace('\n', f'\n{spaces}', -1)


    def to_str(
        self: 'BashStep',
        _python_path: str,
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
            - id: {id}{run_if}
              shell: bash{env}
              run: |-
                {run}
        """
        run_if = _run_if(self.run_if, available_values)
        mapped_args = map_args({}, available_values, input_env)
        env = ''
        if mapped_args:
            arg_lines = '\n'.join([
                f'    {key}: {env_val}'
                for key, env_val in mapped_args.items()
            ])
            env = f'\n  env:\n{arg_lines}'
        return dedent(template).format(
            id=self.id,
            env=env,
            run_if=run_if,
            run=self._sanitize_run(),
        ).rstrip()


class RunStep(BaseModel, Generic[InputModel, OutputModel]):
    """Model used to define a "run" step in a Github action.

    The `id` is important because this is how we will be able to refer to the
    outputs generated by the step. Say our action called other external actions
    such as the cache action. Then if we wanted to pass one of the outputs to
    the cache action we would have to get a handle on the step.

    ```python
    args=SomeInput(some_arg='my_run_step_id.some_output')
    ```

    The `args` should leverage the help of their own input models. All they
    require is that we provide the handle to other outputs from other steps or
    some other values we wish to pass.

    Experiment with different values to see what `action.yaml` generates.
    """

    id: str = Field(description='The id of the step.')

    run_if: str | None = Field(
        default=None,
        description='The condition to run the step.',
    )

    run: Callable[[InputModel], Res[OutputModel]] = Field(
        description='The function passed to [`run_action`][m.github.actions.api.run_action].',
    )

    args: InputModel | None = Field(
        description='The arguments to pass to the run function.',
    )

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
            - id: {id}{run_if}
              shell: bash{env}
              run: PYTHONPATH="$GITHUB_ACTION_PATH{py_path}" python -m {mod}
        """
        run_if = _run_if(self.run_if, available_values)
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
            run_if=run_if,
            py_path=py_path,
            mod=self.run.__module__,
        ).rstrip()


class UsesStep(BaseModel, Generic[InputModel, OutputModel]):
    """A "uses" step in a Github action.

    Model similar to [`RunStep`][m.github.actions.RunStep] but since we do
    not have access to the code that gets executed all we can do is provide the
    `uses` field and our models to describe what the action expects.

    For instance, say we wanted to use the `actions/cache@v4` action. To avoid
    having issues in the future we should create the input and output models
    manually by looking at the documentation
    <https://github.com/actions/cache#inputs>.

    ```python
    class CacheInputs(KebabModel):
        key: str = InArg(help='An explicit key for a cache entry')
        path: str = InArg(help=\"\"\"
            A list of files, directories, and wildcard patterns to cache and
            restore.
        \"\"\")
    ```

    Similarly for the outputs we can define a model. This in the long run should
    help us maintain the composite action better. It is recommended to check the
    inputs and outputs as we update action versions to ensure compatibility.
    """  # noqa: D301, D300 - Angry with slash but we need to escape them

    id: str = Field(description='The step id.')

    run_if: str | None = Field(
        default=None,
        description='The condition to run the step.',
    )

    uses: str = Field(description='A string referencing an action.')

    inputs: type[InputModel] = Field(
        description='A reference to a [KebabModel][m.pydantic.KebabModel] type.',
    )

    outputs: type[OutputModel] = Field(
        description='A reference to a [KebabModel][m.pydantic.KebabModel] type.',
    )

    args: InputModel | None = Field(
        description='The arguments to pass to the action',
    )

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
            - id: {id}{run_if}
              uses: {uses}{env}
        """
        run_if = _run_if(self.run_if, available_values)
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
            run_if=run_if,
            uses=self.uses,
            env=env,
        ).rstrip()


class Action(BaseModel):
    """A Github action.

    The main object to help us define the `actions.yaml` file. Each repository can
    declare several actions. For this reason we can declare the `actions` object as
    a single `Action` or a list of them.

    We could technically do everything in one single step but when we use external
    actions then we are forced to split the step. Note that we have no way of
    having the `if` fields in each step. This is because we are encouraged to handle
    that logic in each of the steps we declare. We have full control of the output to
    `stdout` and `stderr` here.
    """

    file_path: str = Field(description='The full path to the `action.yaml` file.')

    name: str = Field(description='The name of the action.')

    description: str = Field(description='Short description for the action.')

    inputs: type[KebabModel] | None = Field(description="""
        A model describing the inputs for the action. If the action does not
        need inputs then provide `None`. It is important to be explicit in this step
        so that we do not wonder why we cannot use `inputs.[argname]` when we declare a
        step.
    """)

    steps: list[RunStep | UsesStep | BashStep] = Field(
        description='The steps for the action',
    )

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
