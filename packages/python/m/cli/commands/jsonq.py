from typing import Any

from m.cli import (
    Arg,
    command,
    create_issue_handler,
    run_main,
    validate_json_payload,
)
from pydantic import BaseModel


class Arguments(BaseModel):
    r"""Query json data.

    single value::

        m jsonq path.to.property < file.json
        cat file.json | m jsonq path.to.property
        m jsonq @file.json path.to.property

    Return the value stored in the json file. For arrays and objects it
    will print the python representation of the object.

    multiple values::

        m jsonq path1 path2 path3 < file.json
        cat file.json | m jsonq path1 path2 path3
        m jsonq @file.json path1 path2 path3

    use `read` to store in bash variables::

        read -r -d '\n' \
            var1 var2 var3 \
            <<< "$(m jsonq @file.json 'path1' 'path2' 'path3')"

    If available, take advantage of better queries through jq and yq:

    - jq: https://stedolan.github.io/jq/manual/
    - yq: https://mikefarah.gitbook.io/yq/
    """

    payload: Any = Arg(
        default='@-',
        help='json data: @- (stdin), @filename (file), string',
        validator=validate_json_payload,
        positional=True,
    )

    query: list[str] = Arg(
        help='path to json data',
        positional=True,
        nargs='+',
    )

    warn: bool = Arg(
        default=False,
        help='print warning messages instead of errors',
        aliases=['w', 'warn'],
    )

    separator: str = Arg(
        default='\n',
        help='separator for multiple values',
        aliases=['s', 'separator'],
    )


@command(
    help='query json data',
    model=Arguments,
)
def run(arg: Arguments):
    from m.core.json import jsonq

    return run_main(
        lambda: jsonq(arg.payload, arg.separator, *arg.query),
        result_handler=print,
        issue_handler=create_issue_handler(arg.warn),
    )
