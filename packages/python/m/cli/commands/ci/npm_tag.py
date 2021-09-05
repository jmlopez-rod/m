import inspect
import re


def add_parser(sub_parser, raw):
    desc = """
        display an npm tag assigned to given version

        examples:

            ~$ m ci npm_tag 0.0.0-develop.b123
            develop

            ~$ m ci npm_tag 0.0.0-pr1234.b123
            pr1234

            ~$ m ci npm_tag 2.0.1-rc1234.b123
            next

            ~$ m ci npm_tag 2.0.1
            latest
    """
    parser = sub_parser.add_parser(
        'npm_tag',
        help='display an npm tag',
        formatter_class=raw,
        description=inspect.cleandoc(desc),
    )
    parser.add_argument('version', type=str, help='npm package version')


def run(arg):
    regex = r'\d.\d.\d-(.*)\.(.*)'
    matches = re.match(regex, arg.version)
    if matches:
        tag, _ = matches.groups()
        if tag.startswith('rc') or tag.startswith('hotfix'):
            print('next')
        else:
            print(tag)
    else:
        print('latest')
