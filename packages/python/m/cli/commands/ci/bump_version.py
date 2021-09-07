def add_parser(sub_parser, raw):
    parser = sub_parser.add_parser(
        'bump_version',
        help='prompt for the next version',
        formatter_class=raw,
        description='Prompt user for the next valid semantic version',
    )
    add = parser.add_argument
    add(
        '--type',
        required=True,
        choices=['release', 'hotfix'],
        help='verification type',
    )
    add('version', help='version to bump')


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ....core.io import prompt_next_version
    next_ver = prompt_next_version(arg.version, arg.type)
    print(next_ver)  # noqa: WPS421
    return 0
