from m.ci.celt.core import process
from m.ci.celt.core.types import FileReport, Violation

from ...util import FpTestCase


class ProcessTest(FpTestCase):
    """Collection of tests for the celt process module."""

    def test_replace_filenames(self):
        """Replaces filenames that match a given prefix."""
        original = """text path/to/file1.tsx, text path/to/file2.py
        err in path/to/file3.js:1:2 message
        warn in /abs/path/to/file4.jsx:2:4 message
        """
        expected = """text REPO/file1.tsx, text REPO/file2.py
        err in REPO/file3.js:1:2 message
        warn in REPO/file4.jsx:2:4 message
        """
        either = process.replace_filenames(
            original,
            '/abs/path/to|path/to:REPO',
        )
        self.assert_ok(either)
        self.assertEqual(either.value, expected)

    def test_replace_filenames_bad(self):
        """Replaces filenames that match a given prefix."""
        either = process.replace_filenames('irrelevant', '/path')
        self.assert_issue(either, 'file_prefix param missing `:`')

    def test_filter_reports(self):
        """Remove empty reports."""
        reports = [
            FileReport('/path/to/f1.py', []),
            FileReport('/path/to/f2.py', []),
            FileReport('/path/to/fg3.py', [
                Violation('R1', 'm1', 1, 1, '/path/to/fg3.py'),
            ]),
            FileReport('/path/to/f4.py', [
                Violation('R1', 'm1', 1, 1, '/path/to/f4.py'),
            ]),
            FileReport('/path/to/fg5.py', [
                Violation('R1', 'm1', 1, 1, '/path/to/fg5.py'),
            ]),
        ]
        filtered = process.filter_reports(reports)
        self.assertEqual(len(filtered), 3)
        filtered = process.filter_reports(reports, '(.*)/fg(.*).py')
        self.assertEqual(len(filtered), 2)
        files = {x.file_path for x in filtered}
        self.assertTrue({'/path/to/fg3.py', '/path/to/fg5.py'}.issubset(files))

    def test_to_rules_dict(self):
        """Transform a list of rules to a dictionary."""
        reports = [
            FileReport('/path/to/fg3.py', [
                Violation('R1', 'm1', 1, 1, '/path/to/fg3.py'),
                Violation('R2', 'm2', 1, 1, '/path/to/fg3.py'),
            ]),
            FileReport('/path/to/f4.py', [
                Violation('R2', 'm1', 1, 1, '/path/to/f4.py'),
            ]),
            FileReport('/path/to/fg5.py', [
                Violation('R3', 'm1', 1, 1, '/path/to/fg5.py'),
            ]),
        ]
        rules = process.to_rules_dict(reports)
        self.assertEqual(rules, {
            'R1': [reports[0].violations[0]],
            'R2': [reports[0].violations[1], reports[1].violations[0]],
            'R3': [reports[2].violations[0]],
        })
