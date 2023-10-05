from m.core import Good, Res
from m.github.actions import InArg, KebabModel, OutArg, RunStep, run_action


class GithubInputs(KebabModel):
    """Inputs for square_number action."""

    num: str = InArg(help='the number to square')


class SquareNumberOutputs(KebabModel):
    """Outputs for square_number action."""

    num_squared: str = OutArg(help='the number squared', export=True)


def square_number(inputs: GithubInputs) -> Res[SquareNumberOutputs]:
    print('square-number action running')
    num = int(inputs.num)
    return Good(SquareNumberOutputs(num_squared=str(num * num)))


def main_step(
    step_id: str,
    args: GithubInputs,
) -> RunStep[GithubInputs, SquareNumberOutputs]:
    return RunStep[GithubInputs, SquareNumberOutputs](
        id=step_id,
        run=square_number,
        args=args,
    )


if __name__ == '__main__':
    run_action(square_number)
