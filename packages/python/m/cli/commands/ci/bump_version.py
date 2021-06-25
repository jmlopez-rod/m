def add_parser(sub_parser, raw):
    parser = sub_parser.add_parser(
        'bump_version',
        help='prompt for the next version',
        formatter_class=raw,
        description='Prompt user for the next valid semantic version'
    )
    parser.add_argument('version', type=str, help='version to bump')


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ....core.io import prompt_next_version
    next_ver = prompt_next_version(arg.version)
    print(next_ver)
    return 0
