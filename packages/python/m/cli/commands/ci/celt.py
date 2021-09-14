import inspect
import sys
from typing import Tuple, cast

from ....core import one_of
from ...argparse import STORE_TRUE, Arg, add_arguments
from ...utils import display_issue
from ...validators import validate_json_payload, validate_payload

DESC = """
    process the output of a compiler or linter to determine if the ci
    process should stop.

    examples:

        ~$ m ci celt -t eslint -c @config.json < <(eslint [dir] -f json)

        ~$ eslint [...options] > tmp.json
        ~$ m ci celt -t eslint @tmp.json -c '{"allowedEslintRules":{"semi":1}}'

    Depending on the tool that is chosen the configuration should have an
    entry of the form "allowed[ToolName]Rules" or "ignored[ToolName]Rules".
    Only the first letter of the tool should be capitalized to conform to
    the camelcase style.

    The entry should define a map of rule ids to the number of allowed
    violations. In the case of `ignored[ToolName]Rules` we may define
    the rule id and assign an explanation as to why its being ignored.

    In the examples above we use `@config.json`. This means it
    will read the file `config.json`. You can use any file that you want.
    One option is to use eslintrc.json or create a brand new file called
    `allowed_errors.json`.

    Each tool will have different outputs. See below information for each
    tool.

    - eslint: expects json output.

        eslint -f json [dir]

    - pycodestyle: expects default output.

        pycodestyle --format=default [dir]

    - flake8: expects default output.

        flake8 [dir]

    - pylint: expects json output

        pylint -f json --rcfile=[file] [dir]
"""

ARGS: Tuple[Arg, ...] = (
    (
        ['payload'],
        'data: @- (stdin), @filename (file), string. Defaults to @-',
        {'type': validate_payload, 'nargs': '?', 'default': '@-'},
    ),
    (
        ['-t', '--tool'],
        'name of a supported compiler/linter',
        {'required': True},
    ),
    (
        ['-c', '--config'],
        'config data: @filename (file), string',
        {'type': validate_json_payload, 'default': '{}'},  # noqa: P103
    ),
    (
        ['-m', '--max-lines'],
        'max number of error lines to print (Defaults to 5, -1 for all)',
        {'type': int, 'default': 5},
    ),
    (
        ['-r', '--file-regex'],
        'regex expression to filter files',
        {},
    ),
    (
        ['-p', '--file-prefix'],
        "replace file prefix with 'old1|old2:new'",
        {},
    ),
    (
        ['-i', '--ignore-error-allowance'],
        'set every error allowence to 0',
        {**STORE_TRUE},
    ),
    (
        ['-s', '--stats-only'],
        'display a dictionary with current total violations',
        {**STORE_TRUE},
    ),
    (
        ['-f', '--full-message'],
        'display the full error message',
        {**STORE_TRUE},
    ),
    (
        ['--traceback'],
        'display the exception traceback if available',
        {**STORE_TRUE},
    ),
)


def add_parser(sub_parser, raw):
    parser = sub_parser.add_parser(
        'celt',
        help='process the output of compiler/linter',
        formatter_class=raw,
        description=inspect.cleandoc(DESC),
    )
    add_arguments(parser, ARGS)


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ....ci.celt.core.process import PostProcessor
    from ....ci.celt.core.types import Configuration, ProjectStatus
    from ....ci.celt.post_processor import get_post_processor
    from ....core.io import CiTool
    from ....core.issue import Issue

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
    if either.is_bad:
        Issue.show_traceback = arg.traceback
        display_issue(cast(Issue, either.value))
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
        CiTool.error(project.error_msg)
    return project.status.value
