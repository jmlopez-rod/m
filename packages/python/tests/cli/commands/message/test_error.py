import unittest
from io import StringIO
from unittest.mock import patch

from m.__main__ import main


class CliErrorMessageTest(unittest.TestCase):

    @patch('sys.argv', ['m', 'message', 'error', 'error message'])
    @patch('sys.stderr', new_callable=StringIO)
    def test_error_message(self, mock_stderr):
        with self.assertRaises(SystemExit) as prog:
            main()
        self.assertIn('error message\n', mock_stderr.getvalue())
        self.assertEqual(prog.exception.code, 1)

    @patch('sys.argv', ['m', 'message', 'error'])
    @patch('sys.stderr', new_callable=StringIO)
    def test_missing_error_message_cli(self, mock_stderr):
        with self.assertRaises(SystemExit) as prog:
            main()
        self.assertIn(
            'the following arguments are required: message',
            mock_stderr.getvalue(),
        )
        self.assertEqual(prog.exception.code, 2)
