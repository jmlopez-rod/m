import inspect
from typing import cast
from ...validators import validate_json_payload
from ...utils import display_issue


def add_parser(sub_parser, raw):
    desc = """
        process the output of eslint to determine if the ci process should
        stop.

        examples:

            ~$ eslint [dir] -f json | m ci eslint -c @config.json
            ~$ m ci eslint -c @config.json < <(eslint [dir] -f json || echo '')


            ~$ eslint [...options] > tmp.json
            ~$ m ci eslint @tmp.json -c '{"allowedEslintRules":{"semi":1}}'

        This only works as long as the configuration object has
        `allowedEslintRules` defined in it with the number of allowed
        violations. In the examples above we use `@config.json`. This means it
        will read the file `config.json` and it expects `allowedEslintRules`
        to be in there. You can use any file that you want. One option is to
        use eslintrc.json or create a brand new file called
        `allowed_errors.json`.
    """  # noqa
    parser = sub_parser.add_parser(
        'eslint',
        help='process the json output of eslint',
        formatter_class=raw,
        description=inspect.cleandoc(desc)
    )
    parser.add_argument(
        'payload',
        type=validate_json_payload,
        nargs='?',
        default='@-',
        help='json data: @- (stdin), @filename (file), string. Defaults to @-'
    )
    parser.add_argument(
        '-c',
        '--config',
        required=True,
        type=validate_json_payload,
        help='config data: @filename (file), string'
    )
    parser.add_argument(
        '--traceback',
        action='store_true',
        help='display the exception traceback if available'
    )


def run(arg):
    # pylint: disable=import-outside-toplevel
    from ....core.issue import Issue
    from ....ci.linter.eslint import linter as eslint
    from ....ci.linter.status import ProjectStatus

    result = eslint(arg.payload, arg.config)
    if result.is_bad:
        Issue.show_traceback = arg.traceback
        val = cast(Issue, result.value)
        display_issue(val)
        return 1
    return cast(ProjectStatus, result.value).status.value
