from m.cli import Arg, BaseModel, command


class Arguments(BaseModel):
    """Add a log message providing basic information about the devcontainer."""

    img_name: str = Arg(help='name of the docker image', required=True)
    img_version: str = Arg(help='version of the docker image', required=True)
    changelog_url: str | None = Arg(default=None, help='url to the changelog')


@command(
    help='display devcontainer information on start',
    model=Arguments,
)
def run(arg: Arguments) -> int:
    from m.devcontainer.greet import greet

    greet(arg.img_name, arg.img_version, arg.changelog_url)
    return 0
