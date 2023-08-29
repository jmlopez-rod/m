from m.cli import Arg, ArgProxy, BaseModel, command, run_main


class Arguments(BaseModel):
    """Fail command when working on a non valid branch for a release/hotfix.

    Used during a release setup or hotfix setup. We want to make sure
    that we are working on the correct branch depending on release type
    we want to make and the workflow that we are using.
    """

    type: str = ArgProxy(
        '--type',
        required=True,
        choices=['release', 'hotfix'],
        help='verification type',
    )
    m_dir: str = Arg(
        help='m project directory',
        required=True,
        positional=True,
    )


@command(
    help='assert that we are working on the correct branch',
    model=Arguments,
)
def run(arg: Arguments):
    from m.ci.assert_branch import assert_branch

    return run_main(
        lambda: assert_branch(arg.type, arg.m_dir),
        result_handler=lambda _: None,
    )
