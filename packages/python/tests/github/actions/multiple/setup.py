import sys

from m.core import Good, Res
from m.github.actions import InArg, KebabModel, OutArg, RunStep, run_action


class SetupInputs(KebabModel):
    """Setup inputs."""

    setup_in_1: str = InArg(help='setup in 1')
    setup_in_2: str = InArg(help='setup in 2')
    setup_in_3: str = InArg(help='setup in 3', default='setup_in_3')


class SetupOutputs(KebabModel):
    """Setup outputs."""

    setup_out_1: str = OutArg(help='setup out 1', export=True)
    setup_out_2: str = OutArg(help='setup out 2')


def setup(args: SetupInputs) -> Res[SetupOutputs]:
    sys.stdout.write(str(args))
    return Good(SetupOutputs(
        setup_out_1='setup_out_1',
        setup_out_2='setup_out_2',
    ))


def setup_step(step_id: str, args: SetupInputs) -> RunStep[SetupInputs, SetupOutputs]:
    return RunStep[SetupInputs, SetupOutputs](
        id=step_id,
        run=setup,
        args=args,
    )


if __name__ == '__main__':
    run_action(setup)
