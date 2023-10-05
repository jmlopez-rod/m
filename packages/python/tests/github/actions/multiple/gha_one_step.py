from m.github.actions import InArg, KebabModel, OutArg, UsesStep


class ExternalActionInputs(KebabModel):
    """Inputs for gha-one-step action."""

    external_in: str = InArg(help='external in')


class ExternalActionOutputs(KebabModel):
    """Outputs for gha-one-step action."""

    external_1: str = OutArg(help='external 1')
    external_2: str = OutArg(help='external 2')


def gha_one_step(
    id: str,
    args: ExternalActionInputs,
) -> UsesStep[ExternalActionInputs, ExternalActionOutputs]:
    """Create the gha-one-step step.

    Args:
        id: The id of the step.
        args: The inputs for the step.

    Returns:
        The step to run.
    """
    return UsesStep[ExternalActionInputs, ExternalActionOutputs](
        id=id,
        uses='jmlopez-rod/gha-one-step@v0.1.0',
        inputs=ExternalActionInputs,
        outputs=ExternalActionOutputs,
        args=args,
    )
