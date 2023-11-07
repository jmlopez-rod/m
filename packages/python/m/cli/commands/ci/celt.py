import sys
from typing import Any, cast

from m.cli import Arg, BaseModel, command
from m.cli.validators import validate_json_payload, validate_payload
from m.core import Bad, one_of


class Arguments(BaseModel):
    """Process a compiler or linter output to determine if the cli should stop.

    ## Examples

    ```shell
    ~$ m ci celt -t eslint -c @config.json < <(eslint [dir] -f json)

    ~$ eslint [...options] > tmp.json
    ~$ m ci celt -t eslint @tmp.json -c '{"allowedEslintRules":{"semi":1}}'
    ```

    Depending on the tool that is chosen the configuration should have an
    entry of the form `"allowed[ToolName]Rules"` or `"ignored[ToolName]Rules"`.
    Only the first letter of the tool should be capitalized to conform to
    the camel case style.

    The entry should define a map of rule ids to the number of allowed
    violations. In the case of `ignored[ToolName]Rules` we may define
    the rule id and assign an explanation as to why its being ignored.

    In the examples above we use `@config.json`. This means it
    will read the file `config.json`. You can use any file that you want.
    One option is to use eslintrc.json or create a brand new file called
    `allowed_errors.json`.

    ## Tools

    Each tool may provide have different outputs

    ### eslint

    Should be called with the `-f json` option.

    ```bash
    m ci celt -t eslint -c @config.json < <(eslint -f json [dir])
    ```

    ### pycodestyle

    Should be called with the `--format=default` option.

    ```bash
    m ci celt -t pycodestyle -c @config.json < <(pycodestyle --format=default [dir])
    ```

    ### flake8

    Expects default output.

    ```bash
    m ci celt -t flake8 -c @config.json < <(flake8 [dir])
    ```

    ### pylint

    Should be called with the `-f json` option.

    ```bash
    m ci celt -t pylint -c @config.json < <(pylint -f json --rcfile=[file] [dir])
    ```

    ### typescript

    Should be called with the `--pretty false` option.

    ```bash
    m ci celt -t typescript -c @config.json < <(tsc --pretty false)
    ```

    ### ruff

    Should be called with the `--format json` option.

    ```bash
    m ci celt -t ruff -c @config.json < <(ruff check --format json [dir])
    ```
    """

    payload: str = Arg(
        default='@-',
        help="""\
            Output of a compiler or linter. A file may be specified by prefixing
            a filename with `@`. To read from stdin use `@-`.

            Summary: `@-` (stdin), `@filename` (file), `string`.
        """,
        validator=validate_payload,
        positional=True,
    )

    tool: str = Arg(
        help='name of a supported compiler/linter',
        required=True,
        aliases=['t', 'tool'],
    )

    config: Any = Arg(
        default='{}',  # noqa: P103 - json object, not attempting to format
        aliases=['c', 'config'],
        help='config data: @filename (file), string',
        validator=validate_json_payload,
    )

    max_lines: int = Arg(
        default=5,
        aliases=['m', 'max_lines'],
        help='max number of error lines to print, use -1 for all',
    )

    file_regex: str | None = Arg(
        aliases=['r', 'file_regex'],
        help='regex expression to filter files',
    )

    file_prefix: str | None = Arg(
        aliases=['p', 'file_prefix'],
        help="replace file prefix with 'old1|old2:new'",
    )

    ignore_error_allowance: bool = Arg(
        default=False,
        aliases=['i', 'ignore_error_allowance'],
        help='set every error allowance to 0',
    )

    stats_only: bool = Arg(
        default=False,
        aliases=['s', 'stats_only'],
        help='display a dictionary with current total violations',
    )

    full_message: bool = Arg(
        default=False,
        aliases=['f', 'full_message'],
        help='display the full error message',
    )

    traceback: bool = Arg(
        default=False,
        help='display the exception traceback if available',
    )


@command(
    help='process the output of compiler/linter',
    model=Arguments,
)
def run(arg: Arguments):
    from m.ci.celt.core.process import PostProcessor
    from m.ci.celt.core.types import Configuration
    from m.ci.celt.post_processor import get_post_processor
    from m.core.issue import Issue
    from m.log import Logger

    logger = Logger('m.cli.celt')
    config = Configuration(
        arg.max_lines,
        arg.full_message,
        arg.ignore_error_allowance,
        arg.file_regex,
        arg.file_prefix,
    )
    tool_either = get_post_processor(arg.tool, config)
    either = one_of(lambda: [
        project
        for tool in tool_either
        for project in tool.run(arg.payload, arg.config)
    ])
    if isinstance(either, Bad):
        Issue.show_traceback = arg.traceback
        logger.error_block('celt failure', either.value)
        return 1
    # We can do the check for tool_either but the next cast is valid
    # because either would have failed if tool_either was Bad.
    tool = cast(PostProcessor, tool_either.value)
    project = either.value
    output = (
        tool.stats_json(project)
        if arg.stats_only
        else tool.to_str(project)
    )
    print(output, file=sys.stderr)  # noqa: WPS421
    if project.error_msg:
        logger.error(project.error_msg)
    return project.status.value
