import unittest
from io import StringIO
from unittest.mock import patch

from m.__main__ import main
from m.core import Bad, Good


class CliNpmTest(unittest.TestCase):

    @patch('sys.argv', 'm npm clean_tags scope/pkg'.split(' '))
    @patch('sys.stdout', new_callable=StringIO)
    @patch('m.core.subprocess.eval_cmd')
    def test_npm_clean_tags(self, mock_cmd, mock_stdout):
        mock_cmd.side_effect = [
            Good('{"tag1":"","tag2":"","tag3":"v3"}'),
            Good('- tag1'),
            Good('- tag2'),
        ]
        with self.assertRaises(SystemExit) as prog:
            main()
        self.assertEqual(mock_stdout.getvalue(), '["- tag1","- tag2"]\n')
        self.assertEqual(prog.exception.code, 0)

    @patch('sys.argv', 'm npm clean_tags scope/pkg'.split(' '))
    @patch('sys.stderr', new_callable=StringIO)
    @patch('m.core.subprocess.eval_cmd')
    def test_npm_clean_tags_fail(self, mock_cmd, mock_stderr):
        mock_cmd.side_effect = [
            Good('{"tag1":"","tag2":"","tag3":"v3"}'),
            Good('- tag1'),
            Bad('some_error_tag2'),
        ]
        with self.assertRaises(SystemExit) as prog:
            main()
        errors = mock_stderr.getvalue()
        self.assertIn('dist-tag rm issues', errors)
        self.assertIn('some_error_tag2', errors)
        self.assertIn('- tag1', errors)
        self.assertEqual(prog.exception.code, 1)
