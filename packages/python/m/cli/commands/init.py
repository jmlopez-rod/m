from m.cli import command, run_main
from pydantic import BaseModel


class Arguments(BaseModel):
    """Create the necessary files for an m project."""


@command(
    name='init',
    help='initialize an m project',
    model=Arguments,
)
def run():
    import logging

    from m.ci.init import init_repo
    from m.core.logging import logging_config
    logging_config(logging.INFO, [])
    return run_main(init_repo, handle_result=print)
