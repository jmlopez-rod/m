from m.cli.argparse import add_model, cli_options
from m.cli.utils import run_main
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


def add_parser(sub_parser, _raw):
    parser = sub_parser.add_parser('clean_tags', help='remove empty npm tags')
    add_model(parser, Arguments)


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ....npm.clean_tags import clean_tags
    opt = cli_options(Arguments, arg)
    return run_main(lambda: clean_tags(opt.package_name))
