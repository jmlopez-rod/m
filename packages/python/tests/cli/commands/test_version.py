import unittest
from io import StringIO
from unittest.mock import patch

from m.__main__ import main


class CliVersionTest(unittest.TestCase):

    @patch('sys.argv', ['m', '--version'])
    @patch('sys.stdout', new_callable=StringIO)
    def test_m_version(self, mock_stdout):
        with self.assertRaises(SystemExit) as prog:
            main()
        self.assertEqual(mock_stdout.getvalue(), '0.0.0-PLACEHOLDER\n')
        self.assertEqual(prog.exception.code, 0)

    @patch('sys.argv', ['m'])
    @patch('sys.stderr', new_callable=StringIO)
    def test_m_empty_cli(self, mock_stderr):
        with self.assertRaises(SystemExit) as prog:
            main()
        self.assertIn(
            'the following arguments are required: <command>',
            mock_stderr.getvalue(),
        )
        self.assertEqual(prog.exception.code, 2)
