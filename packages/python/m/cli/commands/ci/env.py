from m.cli import command, run_main
from pydantic import BaseModel, Field


class Arguments(BaseModel):
    """Create the [m_dir]/.m/env.list file."""

    m_dir: str = Field(
        description='m project directory',
        positional=True,
        required=True,
    )


@command(
    name='env',
    help='create a list of env variables',
    model=Arguments,
)
def run(arg: Arguments) -> int:
    from m.ci.m_env import write_m_env_vars
    return run_main(lambda: write_m_env_vars(arg.m_dir))
