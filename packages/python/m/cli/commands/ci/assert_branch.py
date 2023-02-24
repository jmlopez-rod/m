from m.cli import add_arg, command, run_main
from pydantic import BaseModel, Field


class Arguments(BaseModel):
    """Fail command when working on a non valid branch for a release/hotfix.

    Used during a release setup or hotfix setup. We want to make sure
    that we are working on the correct branch depending on release type
    we want to make and the workflow that we are using.
    """

    type: str = Field(
        proxy=add_arg(
            '--type',
            required=True,
            choices=['release', 'hotfix'],
            help='verification type',
        ),
    )
    m_dir: str = Field(
        description='m project directory',
        positional=True,
        required=True,
    )


@command(
    name='assert_branch',
    help='assert that we are working on the correct branch',
    model=Arguments,
)
def run(arg: Arguments):
    from m.ci.assert_branch import assert_branch

    return run_main(
        lambda: assert_branch(arg.type, arg.m_dir),
        result_handler=lambda _: None,
    )
