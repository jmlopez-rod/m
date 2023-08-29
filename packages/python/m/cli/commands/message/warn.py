from m.cli import Arg, BaseModel, command


class Arguments(BaseModel):
    """Report a warning.

    example::

        ~$ m message warn 'this is a warning' -f app.js -l 1 -c 5
        ::warning file=app.js,line=1,col=5::Missing semicolon
    """

    message: str = Arg(
        help='warning message',
        positional=True,
        required=True,
    )
    file: str | None = Arg(  # noqa: WPS110 - required by Github
        aliases=['f', 'file'],
        help='filename where warning occurred',
    )
    line: str | None = Arg(
        aliases=['l', 'line'],
        help='line where warning occurred',
    )
    col: str | None = Arg(
        aliases=['c', 'col'],
        help='column where warning occurred',
    )


@command(
    help='report a warning',
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
    Logger('m.cli').warning(msg)
    return 0
