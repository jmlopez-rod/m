from m.cli import Arg, BaseModel, command, run_main


class Arguments(BaseModel):
    """Remove empty npm tags.

        $ m npm clean_tags @scope/package

    When packages are removed there will be empty tags that point to nothing.
    This command will find those empty tags and remove them.
    """

    package_name: str = Arg(
        help='name of the npm package',
        positional=True,
        required=True,
    )


@command(
    help='remove empty npm tags',
    model=Arguments,
)
def run(arg: Arguments):
    from m.npm.clean_tags import clean_tags
    return run_main(lambda: clean_tags(arg.package_name))
