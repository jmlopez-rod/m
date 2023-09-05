from m.cli import Arg, command
from m.core import Good
from m.log import Logger
from pydantic import BaseModel


class Arguments(BaseModel):
    """Verify that the required environment variables are set.

    Exists with non-zero exit code if any of the required environment variables
    are not set.
    """

    env_vars: list[str] = Arg(
        help='environment variables to check',
        nargs='+',
        positional=True,
    )


@command(
    help='require env vars',
    model=Arguments,
)
def run(arg: Arguments):
    from m.devcontainer.env import require_env_vars

    env_res = require_env_vars(arg.env_vars)
    if isinstance(env_res, Good):
        return 0

    logger = Logger(__name__)
    logger.error('missing_env_vars', context=env_res.value.model_dump())
    return 2
