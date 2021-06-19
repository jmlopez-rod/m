import inspect


def add_parser(sub_parser, raw):
    desc = """
        report an error

        Github Actions:
            https://docs.github.com/en/actions/reference/workflow-commands-for-github-actions#setting-an-error-message

        Teamcity:
            https://www.jetbrains.com/help/teamcity/service-messages.html#Reporting+Build+Problems

        example:

            ~$ m message error 'this is an error'
            ::error::this is an error
            ~$ echo $?
            1

        The procedure exits with non-zero code.
    """
    parser = sub_parser.add_parser(
        'error',
        help='report an error',
        formatter_class=raw,
        description=inspect.cleandoc(desc)
    )
    parser.add_argument('message', type=str, help='error message')
    parser.add_argument('--file', type=str, help='filename where error occurred')
    parser.add_argument('--line', type=str, help='line where error occurred')
    parser.add_argument('--col', type=str, help='column where error occurred')


def run(arg):
    # pylint: disable=import-outside-toplevel
    from m.core.io import CiTool
    CiTool.error(arg.message, arg.file, arg.line, arg.col)
    return 1
