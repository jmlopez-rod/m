from m.cli import command, run_main
from pydantic import BaseModel, Field


class Arguments(BaseModel):
    """Remove empty npm tags.

        $ m npm clean_tags @scope/package

    When packages are removed there will be empty tags that point to nothing.
    This command will find those empty tags and remove them.
    """

    package_name: str = Field(
        description='name of the npm package',
        positional=True,
    )


@command(
    name='clean_tags',
    help='remove empty npm tags',
    model=Arguments,
)
def run(arg: Arguments):
    from m.npm.clean_tags import clean_tags
    return run_main(lambda: clean_tags(arg.package_name))
