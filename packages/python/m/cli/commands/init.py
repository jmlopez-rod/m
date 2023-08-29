from m.cli import BaseModel, command, run_main


class Arguments(BaseModel):
    """Create the necessary files for an m project."""


@command(
    help='initialize an m project',
    model=Arguments,
)
def run():
    from m.ci.init import init_repo

    return run_main(init_repo)
