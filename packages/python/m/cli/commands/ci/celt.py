import sys
from typing import Any, cast

from m.cli import command, validate_json_payload, validate_payload
from m.core import is_bad, one_of
from pydantic import BaseModel, Field


class Arguments(BaseModel):
    """Process a compiler or linter output to determine if the cli should stop.

    examples::

        ~$ m ci celt -t eslint -c @config.json < <(eslint [dir] -f json)

        ~$ eslint [...options] > tmp.json
        ~$ m ci celt -t eslint @tmp.json -c '{"allowedEslintRules":{"semi":1}}'

    Depending on the tool that is chosen the configuration should have an
    entry of the form "allowed[ToolName]Rules" or "ignored[ToolName]Rules".
    Only the first letter of the tool should be capitalized to conform to
    the camel case style.

    The entry should define a map of rule ids to the number of allowed
    violations. In the case of `ignored[ToolName]Rules` we may define
    the rule id and assign an explanation as to why its being ignored.

    In the examples above we use `@config.json`. This means it
    will read the file `config.json`. You can use any file that you want.
    One option is to use eslintrc.json or create a brand new file called
    `allowed_errors.json`.

    Each tool will have different outputs. See below information for each
    tool.

    - eslint: expects json output::

        eslint -f json [dir]

    - pycodestyle: expects default output::

        pycodestyle --format=default [dir]

    - flake8: expects default output::

        flake8 [dir]

    - pylint: expects json output::

        pylint -f json --rcfile=[file] [dir]

    - typescript: expects output::

        tsc --pretty false
    """

    payload: str = Field(
        default='@-',
        description='data: @- (stdin), @filename (file), string',
        validator=validate_payload,
        positional=True,
    )

    tool: str = Field(
        aliases=['t', 'tool'],
        description='name of a supported compiler/linter',
        required=True,
    )

    config: Any = Field(
        default='{}',  # noqa: P103 - json object, not attempting to format
        aliases=['c', 'config'],
        description='config data: @filename (file), string',
        validator=validate_json_payload,
    )

    max_lines: int = Field(
        default=5,
        aliases=['m', 'max_lines'],
        description='max number of error lines to print, use -1 for all',
    )

    file_regex: str | None = Field(
        aliases=['r', 'file_regex'],
        description='regex expression to filter files',
    )

    file_prefix: str | None = Field(
        aliases=['p', 'file_prefix'],
        description="replace file prefix with 'old1|old2:new'",
    )

    ignore_error_allowance: bool = Field(
        default=False,
        aliases=['i', 'ignore_error_allowance'],
        description='set every error allowance to 0',
    )

    stats_only: bool = Field(
        default=False,
        aliases=['s', 'stats_only'],
        description='display a dictionary with current total violations',
    )

    full_message: bool = Field(
        default=False,
        aliases=['f', 'full_message'],
        description='display the full error message',
    )

    traceback: bool = Field(
        default=False,
        description='display the exception traceback if available',
    )


@command(
    name='celt',
    help='process the output of compiler/linter',
    model=Arguments,
)
def run(arg: Arguments):
    from m.ci.celt.core.process import PostProcessor
    from m.ci.celt.core.types import Configuration, ProjectStatus
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
    if is_bad(either):
        Issue.show_traceback = arg.traceback
        logger.error_block('celt failure', either.value)
        return 1
    tool = cast(PostProcessor, tool_either.value)
    project = cast(ProjectStatus, either.value)
    output = (
        tool.stats_json(project)
        if arg.stats_only
        else tool.to_str(project)
    )
    print(output, file=sys.stderr)  # noqa: WPS421
    if project.error_msg:
        logger.error(project.error_msg)
    return project.status.value
