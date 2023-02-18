from m.cli import command
from pydantic import BaseModel, Field


class Arguments(BaseModel):
    """Report a warning.

    example::

        ~$ m message warn 'this is a warning' -f app.js -l 1 -c 5
        ::warning file=app.js,line=1,col=5::Missing semicolon
    """

    message: str = Field(
        description='warning message',
        positional=True,
        required=True,
    )
    file: str | None = Field(  # noqa: WPS110 - required by Github
        aliases=['f', 'file'],
        description='filename where warning occurred',
    )
    line: str | None = Field(
        aliases=['l', 'line'],
        description='line where warning occurred',
    )
    col: str | None = Field(
        aliases=['c', 'col'],
        description='column where warning occurred',
    )


@command(
    name='warn',
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
