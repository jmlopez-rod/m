import sys
import unittest
from inspect import cleandoc as cdoc
from io import StringIO
from unittest.mock import patch

from m.__main__ import main


class CliJsonTest(unittest.TestCase):

    @patch('sys.argv', ['m', 'json', '[]'])
    @patch('sys.stdout', new_callable=StringIO)
    @patch.object(sys, 'exit')
    def test_normal(self, mock_exit, mock_stdout):
        main()
        self.assertEqual(mock_stdout.getvalue(), '[]\n')
        mock_exit.assert_called_with(0)

    @patch('sys.argv', [
        'm',
        'json',
        '--sort-keys',
        '{"c": 3, "z": 99, "a": 1}',
    ])
    @patch('sys.stdout', new_callable=StringIO)
    @patch.object(sys, 'exit')
    def test_sort(self, mock_exit, mock_stdout):
        expected = """
        {
          "a": 1,
          "c": 3,
          "z": 99
        }
        """
        main()
        self.assertEqual(mock_stdout.getvalue(), f'{cdoc(expected)}\n')
        mock_exit.assert_called_with(0)
