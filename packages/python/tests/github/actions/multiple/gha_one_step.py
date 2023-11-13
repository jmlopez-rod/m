from m.github.actions import InArg, KebabModel, OutArg, UsesStep


class ExternalActionInputs(KebabModel):
    """Inputs for gha-one-step action."""

    external_in: str = InArg(help='external in')


class ExternalActionOutputs(KebabModel):
    """Outputs for gha-one-step action."""

    external_1: str = OutArg(help='external 1')
    external_2: str = OutArg(help='external 2')


def gha_one_step(
    step_id: str,
    args: ExternalActionInputs,
    run_if: str | None = None,
) -> UsesStep[ExternalActionInputs, ExternalActionOutputs]:
    return UsesStep[ExternalActionInputs, ExternalActionOutputs](
        id=step_id,
        run_if=run_if,
        uses='jmlopez-rod/gha-one-step@v0.1.0',
        inputs=ExternalActionInputs,
        outputs=ExternalActionOutputs,
        args=args,
    )
