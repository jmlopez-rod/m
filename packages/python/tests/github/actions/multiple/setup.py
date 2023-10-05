import sys

from m.core import Good, Res
from m.github.actions import InArg, KebabModel, OutArg, RunStep, run_action


class SetupInputs(KebabModel):
    """Setup inputs."""

    setup_in_1: str = InArg(help='setup in 1')
    setup_in_2: str = InArg(help='setup in 2')


class SetupOutputs(KebabModel):
    """Setup outputs."""

    setup_out_1: str = OutArg(help='setup out 1', export=True)
    setup_out_2: str = OutArg(help='setup out 2')


def setup(args: SetupInputs) -> Res[SetupOutputs]:
    """Setup description.

    Args:
        args: The inputs for the action.

    Returns:
        A `Good` containing the outputs for the action.
    """
    sys.stdout.write(str(args))
    return Good(SetupOutputs(
        setup_out_1='setup_out_1',
        setup_out_2='setup_out_2',
    ))


def setup_step(id: str, args: SetupInputs) -> RunStep[SetupInputs, SetupOutputs]:
    """The main step for the action.

    Args:
        id: The id of the step.
        args: The inputs to the step.

    Returns:
        The step to run.
    """
    return RunStep[SetupInputs, SetupOutputs](
        id=id,
        run=setup,
        args=args,
    )


if __name__ == '__main__':
    run_action(setup)
