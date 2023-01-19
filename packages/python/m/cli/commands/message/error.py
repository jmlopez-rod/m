from m.cli import command
from pydantic import BaseModel, Field


class Arguments(BaseModel):
    """Report an error.

    example::

        ~$ m message error 'this is an error'
        ::error::this is an error
        ~$ echo $?
        1

    The procedure exits with non-zero code.
    """

    message: str = Field(
        description='error message',
        positional=True,
        required=True,
    )
    file: str | None = Field(
        aliases=['f', 'file'],
        description='filename where error occurred',
    )
    line: str | None = Field(
        aliases=['l', 'line'],
        description='line where error occurred',
    )
    col: str | None = Field(
        aliases=['c', 'col'],
        description='column where error occurred',
    )


@command(
    name='error',
    help='report an error',
    model=Arguments,
)
def run(arg: Arguments):
    from m.core.io import get_ci_tool
    get_ci_tool().error(arg.message, arg.file, arg.line, arg.col)
    return 1
