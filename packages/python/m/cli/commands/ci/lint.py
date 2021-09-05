import inspect
import sys
from typing import cast

from ....core import one_of
from ...utils import display_issue
from ...validators import validate_json_payload, validate_payload


def add_parser(sub_parser, raw):
    desc = """
        process the output of a linter to determine if the ci process should
        stop.

        examples:

            ~$ eslint [dir] -f json | m ci lint -t eslint -c @config.json
            ~$ m ci lint -t eslint -c @config.json < <(eslint [dir] -f json || echo '')

            ~$ eslint [...options] > tmp.json
            ~$ m ci lint -t eslint @tmp.json -c '{"allowedEslintRules":{"semi":1}}'

        Depending on the tool that is chosen the configuration should have an
        entry of the form "allowed[ToolName]Rules". Only the first letter
        of the tool should be capitalized to conform to the camelcase style.

        The entry should define a map of rule ids to the number of allowed
        violations.

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

        - pylint: expects json output

            pylint -f json --rcfile=[file] [dir]
    """  # noqa
    parser = sub_parser.add_parser(
        'lint',
        help='process the output of linter',
        formatter_class=raw,
        description=inspect.cleandoc(desc)
    )
    add = parser.add_argument
    add(
        'payload',
        type=validate_payload,
        nargs='?',
        default='@-',
        help='data: @- (stdin), @filename (file), string. Defaults to @-'
    )
    add(
        '-t',
        '--tool',
        required=True,
        help='name of a supported linter'
    )
    add(
        '-c',
        '--config',
        default='{}',
        type=validate_json_payload,
        help='config data: @filename (file), string'
    )
    add(
        '-m',
        '--max-lines',
        default=5,
        type=int,
        help='maximum number of lines to print per error'
    )
    add(
        '--traceback',
        action='store_true',
        help='display the exception traceback if available'
    )


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ....ci.linter import get_linter
    from ....ci.linter.status import ProjectStatus
    from ....core.issue import Issue

    result = one_of(lambda: [
        res
        for linter in get_linter(arg.tool, arg.max_lines)
        for res in linter(arg.payload, arg.config, sys.stdout)
    ])
    if result.is_bad:
        Issue.show_traceback = arg.traceback
        val = cast(Issue, result.value)
        display_issue(val)
        return 1
    return cast(ProjectStatus, result.value).status.value
