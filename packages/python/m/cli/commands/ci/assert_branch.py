import inspect

from ...utils import run_main


def add_parser(sub_parser, raw):
    desc = """
        Used during a release setup or hotfix setup. We want to make sure
        that we are working on the correct branch depending on verification
        we want to make and the workflow that we are using.
    """
    parser = sub_parser.add_parser(
        'assert_branch',
        help='assert that we are working on the correct branch',
        formatter_class=raw,
        description=inspect.cleandoc(desc),
    )
    add = parser.add_argument
    add(
        '--type',
        required=True,
        choices=['release', 'hotfix'],
        help='verification type',
    )
    add('m_dir', type=str, help='m project directory')


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ....ci.assert_branch import assert_branch
    return run_main(lambda: assert_branch(arg.type, arg.m_dir))
