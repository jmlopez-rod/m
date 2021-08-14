import json
from typing import cast, List
from io import StringIO

from m.ci.linter.eslint import linter as eslint
from m.ci.linter.status import ProjectStatus, ExitCode
from ..util import FpTestCase, read_fixture


def assert_str_has(content: str, substrings: List[str]):
    missing = [x for x in substrings if x not in content]
    if len(missing) > 0:
        raise AssertionError(f'missing {missing}')


class EslintTest(FpTestCase):
    def test_eslint_fail(self):
        with StringIO() as io_stream:
            payload = read_fixture('eslint_payload.json')
            result = eslint(json.loads(payload), {}, io_stream)
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
                }
            }
            result = eslint(json.loads(payload), config, io_stream)
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
            result = eslint(json.loads(payload), config, io_stream)
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
            result = eslint(json.loads(payload), config, io_stream)
            self.assert_ok(result)
            status = cast(ProjectStatus, result.value)
            self.assertEqual(status.status, ExitCode.OK)
            assert_str_has(io_stream.getvalue(), [
                'project has 5 errors to clear'
            ])

    def test_eslint_no_errors(self):
        with StringIO() as io_stream:
            payload = read_fixture('eslint_payload_clear.json')
            result = eslint(json.loads(payload), {}, io_stream)
            self.assert_ok(result)
            status = cast(ProjectStatus, result.value)
            self.assertEqual(status.status, ExitCode.OK)
            assert_str_has(io_stream.getvalue(), [
                'no errors found'
            ])
