from ...utils import run_main


def add_parser(sub_parser, raw):
    parser = sub_parser.add_parser(
        'env',
        help='create a list of env variables',
        formatter_class=raw,
        description='Create the [m_dir]/.m/env.list file',
    )
    add = parser.add_argument
    add('m_dir', type=str, help='m project directory')


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ....ci.m_env import write_m_env_vars
    return run_main(lambda: write_m_env_vars(arg.m_dir))
