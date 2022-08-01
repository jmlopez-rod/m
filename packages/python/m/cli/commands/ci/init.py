from ...utils import run_main


def add_parser(sub_parser, raw):
    sub_parser.add_parser(
        'init',
        help='initialize an m project',
        formatter_class=raw,
        description='Create the necessary files for an m project.',
    )


def run(_arg):
    # pylint: disable=import-outside-toplevel
    from ....ci.init import init_repo
    return run_main(init_repo)
