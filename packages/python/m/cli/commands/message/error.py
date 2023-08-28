from m.cli import Arg, BaseModel, command


class Arguments(BaseModel):
    """Report an error.

    example::

        ~$ m message error 'this is an error'
        ::error::this is an error
        ~$ echo $?
        1

    The procedure exits with non-zero code.
    """

    message: str = Arg(
        help='error message',
        positional=True,
        required=True,
    )
    file: str | None = Arg(  # noqa: WPS110 - required by Github
        aliases=['f', 'file'],
        help='filename where error occurred',
    )
    line: str | None = Arg(
        aliases=['l', 'line'],
        help='line where error occurred',
    )
    col: str | None = Arg(
        aliases=['c', 'col'],
        help='column where error occurred',
    )


@command(
    help='report an error',
    model=Arguments,
)
def run(arg: Arguments):
    from m.log import Logger, Message

    msg = Message(
        msg=arg.message,
        file=arg.file,
        line=arg.line,
        col=arg.col,
    )
    Logger('m.cli').error(msg)
    return 1
