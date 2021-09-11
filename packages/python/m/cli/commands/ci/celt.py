import sys
import inspect
from typing import cast

from ....core import one_of
from ...utils import display_issue
from ...validators import validate_json_payload, validate_payload


def add_parser(sub_parser, raw):
    desc = """
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
    """  # noqa
    parser = sub_parser.add_parser(
        'celt',
        help='process the output of compiler/linter',
        formatter_class=raw,
        description=inspect.cleandoc(desc),
    )
    add = parser.add_argument
    add(
        'payload',
        type=validate_payload,
        nargs='?',
        default='@-',
        help='data: @- (stdin), @filename (file), string. Defaults to @-',
    )
    add(
        '-t',
        '--tool',
        required=True,
        help='name of a supported compiler/linter',
    )
    add(
        '-c',
        '--config',
        default='{}',
        type=validate_json_payload,
        help='config data: @filename (file), string',
    )
    add(
        '-m',
        '--max-lines',
        default=5,
        type=int,
        help='maximum number of lines to print per error',
    )
    add(
        '-f',
        '--full-message',
        action='store_true',
        help='display the full error message',
    )
    add('-r', '--file-regex', help='regex expression to filter files')
    add('-p', '--file-prefix', help="replace file prefix with 'old1|old2:new'")
    add(
        '-s',
        '--stats-only',
        action='store_true',
        help="display a dictionary with current total violations"
    )
    add(
        '--traceback',
        action='store_true',
        help='display the exception traceback if available',
    )


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ....ci.celt.post_processor import get_post_processor
    from ....ci.celt.core.process import PostProcessor
    from ....ci.celt.core.types import ProjectStatus, Configuration
    from ....core.issue import Issue
    from ....core.io import CiTool

    config = Configuration(
        arg.max_lines,
        arg.full_message,
        arg.file_regex,
        arg.file_prefix,
    )
    tool_either = get_post_processor(arg.tool, config)
    result = one_of(
        lambda: [
            project
            for tool in tool_either
            for project in tool.run(arg.payload, arg.config)
        ],
    )
    if result.is_bad:
        Issue.show_traceback = arg.traceback
        val = cast(Issue, result.value)
        display_issue(val)
        return 1
    tool = cast(PostProcessor, tool_either.value)
    project = cast(ProjectStatus, result.value)
    output = (
        tool.stats_json(project)
        if arg.stats_only
        else tool.to_str(project)
    )
    print(output, file=sys.stderr)  # noqa: WPS421
    if project.error_msg:
        CiTool.error(project.error_msg)
    return project.status.value
