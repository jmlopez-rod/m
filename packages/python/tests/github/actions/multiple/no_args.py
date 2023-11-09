import sys

from m.core import Good, Res
from m.github.actions import KebabModel, RunStep, run_action


def no_args(args: KebabModel) -> Res[KebabModel]:
    """No args description.

    Args:
        args: The inputs for the action.

    Returns:
        A `Good` containing the outputs for the action.
    """
    sys.stdout.write(str(args))
    return Good(KebabModel())


def no_args_step(step_id: str) -> RunStep[KebabModel, KebabModel]:
    return RunStep[KebabModel, KebabModel](
        id=step_id,
        run=no_args,
        args=None,
    )


if __name__ == '__main__':
    run_action(no_args)
