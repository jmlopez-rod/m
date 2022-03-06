from .cli.utils import run_cli
from .version import VERSION


def main_args(argp):
    argp.add_argument('--version', action='version', version=VERSION)


def main():
    run_cli(__file__, main_args)


if __name__ == '__main__':  # pragma: no cover
    main()
