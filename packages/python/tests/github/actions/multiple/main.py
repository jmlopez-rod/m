import sys

from m.core import Good, Res
from m.github.actions import InArg, KebabModel, OutArg, RunStep, run_action


class MainInputs(KebabModel):
    """Main inputs."""

    main_in: str = InArg(help='main 1')


class MainOutputs(KebabModel):
    """Main outputs."""

    main_1: str = OutArg(help='main 1', export=True)
    main_2: str = OutArg(help='main 2', export=True)


def main(inputs: MainInputs) -> Res[MainOutputs]:
    """Main description."""  # noqa: DAR201 - github actions format
    sys.stdout.write(str(inputs))
    return Good(MainOutputs(
        main_1='main_out_1',
        main_2='main_out_2',
    ))


def main_step(id: str, args: MainInputs) -> RunStep[MainInputs, MainOutputs]:
    return RunStep[MainInputs, MainOutputs](
        id=id,
        run=main,
        args=args,
    )


if __name__ == '__main__':
    run_action(main)
