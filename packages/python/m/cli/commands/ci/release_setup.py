from m.cli import command, run_main
from pydantic import BaseModel, Field


class Arguments(BaseModel):
    """Update the config and changelog files."""

    changelog: str = Field(
        default='CHANGELOG.md',
        description='CHANGELOG filename',
    )
    m_dir: str = Field(
        description='m project directory',
        positional=True,
        required=True,
    )
    new_ver: str = Field(
        description='the new version',
        positional=True,
        required=True,
    )


@command(
    name='release_setup',
    help='modify the config and changelog files',
    model=Arguments,
)
def run(arg: Arguments) -> int:
    from m.ci.release_setup import release_setup
    return run_main(
        lambda: release_setup(
            arg.m_dir,
            None,
            arg.new_ver,
            arg.changelog,
        ),
    )
