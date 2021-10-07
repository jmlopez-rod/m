import inspect
from typing import List, cast

from m.ci.celt.core.process import PostProcessor
from m.ci.celt.core.types import Configuration, ExitCode, ProjectStatus
from m.ci.celt.post_processor import get_post_processor

from ...util import FpTestCase, read_fixture


def assert_str_has(content: str, substrings: List[str]):
    """Assert that a string has a set of substrings.

    Args:
        content: The string to test.
        substrings: The required strings to appear in `content`.
    """
    missing = [x for x in substrings if x not in content]
    if len(missing) > 0:
        raise AssertionError(f'missing {missing}')


def _post_processor(name: str) -> PostProcessor:
    celt_config = Configuration()
    return cast(PostProcessor, get_post_processor(name, celt_config).value)


class CeltTest(FpTestCase):
    def test_unknown_post_processor_fail(self):
        eslint = get_post_processor('unknown', Configuration())
        self.assert_issue(eslint, 'unknown is not a supported post processor')

    def test_eslint_fail(self):
        eslint = _post_processor('eslint')
        payload = read_fixture('eslint_payload.json')
        result = eslint.run(payload, {})
        self.assert_ok(result)
        project = cast(ProjectStatus, result.value)
        self.assertEqual(project.status, ExitCode.error)
        assert_str_has(eslint.to_str(project), [
            'no-unused-vars (found 3, allowed 0)',
            'quotes (found 1, allowed 0)',
            'semi (found 1, allowed 0)',
        ])
        self.assertEqual(project.error_msg, '5 extra errors were introduced')
        # test json stats
        json_stats = eslint.stats_json(project)
        expected = """
            {
              "allowedEslintRules": {
                "semi": 1,
                "quotes": 1,
                "no-unused-vars": 3
              }
            }
        """
        self.assertEqual(json_stats, inspect.cleandoc(expected))

    def test_eslint_fail_errors(self):
        eslint = _post_processor('eslint')
        payload = read_fixture('eslint_payload.json')
        config = {
            'allowedEslintRules': {
                'no-unused-vars': 3,
                'semi': 1,
                'made-up': 100,
            }
        }
        result = eslint.run(payload, config)
        self.assert_ok(result)
        project = cast(ProjectStatus, result.value)
        self.assertEqual(project.status, ExitCode.error)
        assert_str_has(eslint.to_str(project), [
            'no-unused-vars      3        3',
            'quotes (found 1, allowed 0)',
        ])
        self.assertEqual(project.error_msg, '1 extra errors were introduced')
        # Ignoring the configuration - See all errors
        eslint.celt_config.ignore_error_allowance = True
        result = eslint.run(payload, config)
        self.assert_ok(result)
        project = cast(ProjectStatus, result.value)
        self.assertEqual(project.status, ExitCode.error)
        assert_str_has(eslint.to_str(project), [
            'no-unused-vars      3        0'
        ])

    def test_eslint_fail_reduce(self):
        eslint = _post_processor('eslint')
        payload = read_fixture('eslint_payload.json')
        config = {
            'allowedEslintRules': {
                'no-unused-vars': 5,
                'quotes': 1,
                'semi': 10,
            }
        }
        result = eslint.run(payload, config)
        self.assert_ok(result)
        project = cast(ProjectStatus, result.value)
        self.assertEqual(project.status, ExitCode.needs_readjustment)
        self.assertEqual(
            project.error_msg,
            '11 errors were removed - lower error allowance',
        )

    def test_eslint_ok(self):
        eslint = _post_processor('eslint')
        payload = read_fixture('eslint_payload.json')
        config = {
            'allowedEslintRules': {
                'no-unused-vars': 3,
                'quotes': 1,
                'semi': 1,
            }
        }
        result = eslint.run(payload, config)
        self.assert_ok(result)
        project = cast(ProjectStatus, result.value)
        self.assertEqual(project.status, ExitCode.ok)
        assert_str_has(eslint.to_str(project), [
            'project has 5 errors to clear',
        ])

    def test_eslint_no_errors(self):
        eslint = _post_processor('eslint')
        payload = read_fixture('eslint_payload_clear.json')
        result = eslint.run(payload, {})
        self.assert_ok(result)
        project = cast(ProjectStatus, result.value)
        self.assertEqual(project.status, ExitCode.ok)
        assert_str_has(eslint.to_str(project), [
            'no errors found'
        ])
        # test json stats
        json_stats = eslint.stats_json(project)
        expected = """
            {
              "allowedEslintRules": {
              }
            }
        """
        self.assertEqual(json_stats, inspect.cleandoc(expected))


    def test_eslint_no_errors_reduce(self):
        eslint = _post_processor('eslint')
        payload = read_fixture('eslint_payload_clear.json')
        config = {'allowedEslintRules': {'semi': 10, 'other': 5}}
        result = eslint.run(payload, config)
        self.assert_ok(result)
        project = cast(ProjectStatus, result.value)
        self.assertEqual(project.status, ExitCode.needs_readjustment)
        self.assertEqual(
            project.error_msg,
            '15 errors were removed - lower error allowance',
        )

    def test_pycodestyle_fail(self):
        pycodestyle = _post_processor('pycodestyle')
        payload = read_fixture('pycodestyle_payload.txt')
        result = pycodestyle.run(payload, {})
        self.assert_ok(result)
        project = cast(ProjectStatus, result.value)
        self.assertEqual(project.status, ExitCode.error)
        assert_str_has(pycodestyle.to_str(project), [
            'E303 (found 1, allowed 0)',
            'E201 (found 1, allowed 0)',
            'E202 (found 1, allowed 0)',
            'E271 (found 1, allowed 0)',
            'E203 (found 1, allowed 0)',
        ])
        self.assertEqual(
            project.error_msg,
            '5 extra errors were introduced',
        )

    def test_pylint_fail_bad_json(self):
        pylint = _post_processor('pylint')
        result = pylint.run('bad_json', {})
        self.assert_issue(result, 'failed to parse the json data')

    def test_pylint_fail(self):
        pylint = _post_processor('pylint')
        payload = read_fixture('pylint_payload.json')
        result = pylint.run(payload, {})
        self.assert_ok(result)
        project = cast(ProjectStatus, result.value)
        self.assertEqual(project.status, ExitCode.error)
        output = pylint.to_str(project)
        assert_str_has(output, [
            'missing-function-docstring (found 1, allowed 0)',
            'import-outside-toplevel (found 1, allowed 0)',
        ])
        self.assertNotIn('long message', output)
        self.assertEqual(
            project.error_msg,
            '2 extra errors were introduced',
        )

    def test_pylint_fail_full_message(self):
        pylint = _post_processor('pylint')
        payload = read_fixture('pylint_payload.json')
        pylint.celt_config.full_message = True
        result = pylint.run(payload, {})
        self.assert_ok(result)
        project = cast(ProjectStatus, result.value)
        self.assertEqual(project.status, ExitCode.error)
        output = pylint.to_str(project)
        assert_str_has(output, [
            'missing-function-docstring (found 1, allowed 0)',
            'import-outside-toplevel (found 1, allowed 0)',
            'long message',
        ])

    def test_pylint_fail_max_lines(self):
        pylint = _post_processor('pylint')
        payload = read_fixture('pylint_payload.json')
        pylint.celt_config.max_lines = 0
        result = pylint.run(payload, {})
        self.assert_ok(result)
        project = cast(ProjectStatus, result.value)
        self.assertEqual(project.status, ExitCode.error)
        output = pylint.to_str(project)
        assert_str_has(output, [
            'missing-function-docstring (found 1, allowed 0)',
            'import-outside-toplevel (found 1, allowed 0)',
            '... and 1 more',
        ])

    def test_pylint_fail_order(self):
        pylint = _post_processor('pylint')
        payload = read_fixture('pylint_payload_order.json')
        result = pylint.run(payload, {})
        self.assert_ok(result)
        project = cast(ProjectStatus, result.value)
        self.assertEqual(project.status, ExitCode.error)
        output = pylint.to_str(project)
        assert_str_has(output, [
            'missing-function-docstring (found 1, allowed 0)',
            'import-outside-toplevel (found 2, allowed 0)',
        ])
        expected = inspect.cleandoc('''
            missing-function-docstring      1        0
            import-outside-toplevel         2        0
        ''').strip()
        self.assertIn(expected, output)
        self.assertEqual(
            project.error_msg,
            '3 extra errors were introduced',
        )

    def test_pycodestyle_ignored(self):
        pycodestyle = _post_processor('pycodestyle')
        payload = read_fixture('pycodestyle_payload.txt')
        result = pycodestyle.run(
            payload,
            {'ignoredPycodestyleRules': {'E201': 'reason'}},
        )
        self.assert_ok(result)
        project = cast(ProjectStatus, result.value)
        self.assertEqual(project.status, ExitCode.error)
        assert_str_has(pycodestyle.to_str(project), [
            'E303 (found 1, allowed 0)',
            'E201 (found 1, IGNORED)',
            'E202 (found 1, allowed 0)',
            'E271 (found 1, allowed 0)',
            'E203 (found 1, allowed 0)',
        ])
        self.assertEqual(
            project.error_msg,
            '4 extra errors were introduced',
        )
