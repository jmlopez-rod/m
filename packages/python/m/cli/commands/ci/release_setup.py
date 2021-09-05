from ...utils import run_main


def add_parser(sub_parser, raw):
    parser = sub_parser.add_parser(
        'release_setup',
        help='modify the config and changelog files',
        formatter_class=raw,
        description='Update the config and changelog files',
    )
    add = parser.add_argument
    add(
        '--changelog',
        type=str,
        default='CHANGELOG.md',
        help='CHANGELOG filename',
    )
    add('m_dir', type=str, help='m project directory')
    add('new_ver', type=str, help='the new version')


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ....ci.release_setup import release_setup
    return run_main(
        lambda: release_setup(
            arg.m_dir,
            arg.new_ver,
            arg.changelog,
        ),
    )
