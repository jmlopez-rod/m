import sys
import unittest
from io import StringIO
from unittest.mock import patch

from m.__main__ import main


class CliJsonQTest(unittest.TestCase):

    @patch('sys.argv', ['m', 'jsonq', '[1]', '0'])
    @patch('sys.stdout', new_callable=StringIO)
    @patch.object(sys, 'exit')
    def test_access_array(self, mock_exit, mock_stdout):
        main()
        self.assertEqual(mock_stdout.getvalue(), '1\n')
        mock_exit.assert_called_with(0)

    @patch('sys.argv', [
        'm',
        'jsonq',
        '{"a":{"b":{"c":["hello"] } } }',
        'a.b.c.0',
    ])
    @patch('sys.stdout', new_callable=StringIO)
    @patch.object(sys, 'exit')
    def test_access_nested(self, mock_exit, mock_stdout):
        main()
        self.assertEqual(mock_stdout.getvalue(), 'hello\n')
        mock_exit.assert_called_with(0)

    @patch('sys.argv', [
        'm',
        'jsonq',
        '{"a":{"b":{"c":["hello"]}}}',
        'a.b.d.0',
    ])
    @patch('sys.stderr', new_callable=StringIO)
    @patch.object(sys, 'exit')
    def test_error(self, mock_exit, mock_stderr):
        main()
        errors = mock_stderr.getvalue()
        self.assertIn('multi_get key retrieval failure', errors)
        self.assertIn('key lookup failure: `a.b.d.0`', errors)
        mock_exit.assert_called_with(1)
