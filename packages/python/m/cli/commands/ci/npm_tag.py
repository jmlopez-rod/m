from m.cli import command
from pydantic import BaseModel, Field


class Arguments(BaseModel):
    """Display an npm tag assigned to given version.

    examples::

        ~$ m ci npm_tag 0.0.0-develop.b123
        develop

        ~$ m ci npm_tag 0.0.0-pr1234.b123
        pr1234

        ~$ m ci npm_tag 2.0.1-rc1234.b123
        next

        ~$ m ci npm_tag 2.0.1
        latest
    """

    npm_tag: str = Field(
        description='npm package version',
        positional=True,
        required=True,
    )


@command(
    name='npm_tag',
    help='display an npm tag',
    model=Arguments,
)
def run(arg: Arguments):
    from m.npm.tag import npm_tags

    print(npm_tags(arg.npm_tag)[0])  # noqa: WPS421
    return 0
