import inspect
from io import StringIO
from typing import List, cast

from m.ci.linter.eslint import read_payload as read_eslint_payload
from m.ci.linter.pycodestyle import read_payload as read_pycodestyle_payload
from m.ci.linter.pylint import read_payload as read_pylint_payload
from m.ci.linter.status import ExitCode, ProjectStatus, linter

from ..util import FpTestCase, read_fixture

eslint = linter('eslint', 5, read_eslint_payload)
pycodestyle = linter('pycodestyle', 5, read_pycodestyle_payload)
pylint = linter('pylint', 5, read_pylint_payload)


def assert_str_has(content: str, substrings: List[str]):
    missing = [x for x in substrings if x not in content]
    if len(missing) > 0:
        raise AssertionError(f'missing {missing}')


class LintTest(FpTestCase):
    def test_eslint_fail(self):
        with StringIO() as io_stream:
            payload = read_fixture('eslint_payload.json')
            result = eslint(payload, {}, io_stream)
            self.assert_ok(result)
            status = cast(ProjectStatus, result.value)
            self.assertEqual(status.status, ExitCode.ERROR)
            assert_str_has(io_stream.getvalue(), [
                'no-unused-vars (found 3, allowed 0)',
                'quotes (found 1, allowed 0)',
                'semi (found 1, allowed 0)',
                '5 extra errors were introduced',
            ])

    def test_eslint_fail_errors(self):
        with StringIO() as io_stream:
            payload = read_fixture('eslint_payload.json')
            config = {
                'allowedEslintRules': {
                    'no-unused-vars': 3,
                    'semi': 1,
                    'made-up': 100,
                }
            }
            result = eslint(payload, config, io_stream)
            self.assert_ok(result)
            status = cast(ProjectStatus, result.value)
            self.assertEqual(status.status, ExitCode.ERROR)
            assert_str_has(io_stream.getvalue(), [
                'quotes (found 1, allowed 0)',
                '1 extra errors were introduced'
            ])

    def test_eslint_fail_reduce(self):
        with StringIO() as io_stream:
            payload = read_fixture('eslint_payload.json')
            config = {
                'allowedEslintRules': {
                    'no-unused-vars': 5,
                    'quotes': 1,
                    'semi': 10,
                }
            }
            result = eslint(payload, config, io_stream)
            self.assert_ok(result)
            status = cast(ProjectStatus, result.value)
            self.assertEqual(status.status, ExitCode.NEEDS_READJUSTMENT)
            assert_str_has(io_stream.getvalue(), [
                '11 errors were removed - lower error allowance'
            ])

    def test_eslint_ok(self):
        with StringIO() as io_stream:
            payload = read_fixture('eslint_payload.json')
            config = {
                'allowedEslintRules': {
                    'no-unused-vars': 3,
                    'quotes': 1,
                    'semi': 1,
                }
            }
            result = eslint(payload, config, io_stream)
            self.assert_ok(result)
            status = cast(ProjectStatus, result.value)
            self.assertEqual(status.status, ExitCode.OK)
            assert_str_has(io_stream.getvalue(), [
                'project has 5 errors to clear'
            ])

    def test_eslint_no_errors(self):
        with StringIO() as io_stream:
            payload = read_fixture('eslint_payload_clear.json')
            result = eslint(payload, {}, io_stream)
            self.assert_ok(result)
            status = cast(ProjectStatus, result.value)
            self.assertEqual(status.status, ExitCode.OK)
            assert_str_has(io_stream.getvalue(), [
                'no errors found'
            ])

    def test_eslint_no_errors_reduce(self):
        with StringIO() as io_stream:
            payload = read_fixture('eslint_payload_clear.json')
            config = {'allowedEslintRules': {'semi': 10, 'other': 5}}
            result = eslint(payload, config, io_stream)
            self.assert_ok(result)
            status = cast(ProjectStatus, result.value)
            self.assertEqual(status.status, ExitCode.NEEDS_READJUSTMENT)
            assert_str_has(io_stream.getvalue(), [
                '15 errors were removed - lower error allowance'
            ])

    def test_pycodestyle_fail(self):
        with StringIO() as io_stream:
            payload = read_fixture('pycodestyle_payload.txt')
            result = pycodestyle(payload, {}, io_stream)
            self.assert_ok(result)
            status = cast(ProjectStatus, result.value)
            self.assertEqual(status.status, ExitCode.ERROR)
            assert_str_has(io_stream.getvalue(), [
                'E303 (found 1, allowed 0)',
                'E201 (found 1, allowed 0)',
                'E202 (found 1, allowed 0)',
                'E271 (found 1, allowed 0)',
                'E203 (found 1, allowed 0)',
                '5 extra errors were introduced',
            ])

    def test_pylint_fail(self):
        with StringIO() as io_stream:
            payload = read_fixture('pylint_payload.json')
            result = pylint(payload, {}, io_stream)
            self.assert_ok(result)
            status = cast(ProjectStatus, result.value)
            self.assertEqual(status.status, ExitCode.ERROR)
            output = io_stream.getvalue()
            assert_str_has(output, [
                'missing-function-docstring (found 1, allowed 0)',
                'import-outside-toplevel (found 1, allowed 0)',
                '2 extra errors were introduced',
            ])
            self.assertNotIn('long message', output)

    def test_pylint_fail_order(self):
        with StringIO() as io_stream:
            payload = read_fixture('pylint_payload_order.json')
            result = pylint(payload, {}, io_stream)
            self.assert_ok(result)
            status = cast(ProjectStatus, result.value)
            self.assertEqual(status.status, ExitCode.ERROR)
            output = io_stream.getvalue()
            assert_str_has(output, [
                'missing-function-docstring (found 1, allowed 0)',
                'import-outside-toplevel (found 2, allowed 0)',
                '3 extra errors were introduced',
            ])
            expected = inspect.cleandoc('''
                missing-function-docstring      1        0
                import-outside-toplevel         2        0
            ''').strip()
            self.assertIn(expected, output)
