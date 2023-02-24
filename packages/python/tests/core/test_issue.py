import unittest
from contextlib import suppress

from m.core import Bad, Issue, issue


class IssueTest(unittest.TestCase):
    def test_instances(self):
        obj = Issue('message').to_dict()
        self.assertEqual(obj.get('message'), 'message')
        self.assertIsNotNone(obj.get('traceback'))
        self.assertIsNone(obj.get('description'))
        self.assertIsNone(obj.get('cause'))
        self.assertIsNone(obj.get('data'))

    def test_description(self):
        obj = Issue('message', description='desc').to_dict()
        self.assertEqual(obj.get('message'), 'message')
        self.assertEqual(obj.get('description'), 'desc')
        self.assertIsNotNone(obj.get('traceback'))
        self.assertIsNone(obj.get('cause'))
        self.assertIsNone(obj.get('data'))

    def test_init_param_order(self):
        obj = Issue(
            description='desc',
            message='message',
            cause=ValueError('cause'),
            context={'x': 100},
        ).to_dict()
        self.assertEqual(obj.get('message'), 'message')
        self.assertEqual(obj.get('description'), 'desc')
        self.assertIsNotNone(obj.get('cause'))
        self.assertIsNotNone(obj.get('context'))

    def test_one_of(self):
        obj = issue('message')
        self.assertIsInstance(obj, Bad)
        self.assertEqual(obj.value.message, 'message')


def test_issue_remove_traceback():
    sub = Issue(
        message='sub',
        description='sub',
        cause=ValueError('sub-cause'),
    )
    obj = Issue(
        description='desc',
        message='message',
        cause=sub,
        context=dict(x=100),
    )
    str_obj = obj.to_str(show_traceback=False)
    assert 'traceback' not in str_obj

    str_obj = obj.to_str(show_traceback=True)
    assert 'traceback' in str_obj


def test_issue_yaml():
    exception = ValueError('sub-cause')
    sub = Issue(
        message='sub',
        description='sub',
        cause=exception,
    )
    tuple_data = ('one', 'two')
    obj = Issue(
        description='desc',
        message='message',
        cause=sub,
        # covers displaying tuple_data
        context={'x': 100, 'tuple_data': tuple_data},
    )
    Issue.yaml_traceback = True
    str_obj = ''
    with suppress(BaseException):
        str_obj = f'{obj}'
    Issue.yaml_traceback = False
    # asserting that we have the message of the ValueError
    # also making sure we get some colors
    assert "one" in str_obj
    assert "two" in str_obj
    assert '\x1b[38;5;153msub-cause\x1b[39m\n' in str_obj
