from m.core import Good, Res
from m.github.actions import InArg, KebabModel, OutArg, RunStep, run_action


class GithubInputs(KebabModel):
    """Inputs for square_number action."""

    num: str = InArg(help='the number to square')


class SquareNumberOutputs(KebabModel):
    """Outputs for square_number action."""

    num_squared: str = OutArg(help='the number squared', export=True)


def square_number(inputs: GithubInputs) -> Res[SquareNumberOutputs]:
    """Description for action can be written here.

    Args:
        inputs: The inputs for the action.

    Returns:
        A `Good` containing the outputs for the action.
    """
    num = int(inputs.num)
    return Good(SquareNumberOutputs(num_squared=str(num * num)))


def main_step(
    id: str,
    args: GithubInputs
) -> RunStep[GithubInputs, SquareNumberOutputs]:
    """The main step for the action.

    Args:
        id: The id of the step.
        args: The inputs for the step.

    Returns:
        The step to run.
    """
    return  RunStep[GithubInputs, SquareNumberOutputs](
        id=id,
        run=square_number,
        args=args,
    )


if __name__ == '__main__':
    run_action(square_number)
