import unittest
from m.core import issue, Issue, Bad


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
            data=dict(x=100),
        ).to_dict()
        self.assertEqual(obj.get('message'), 'message')
        self.assertEqual(obj.get('description'), 'desc')
        self.assertIsNotNone(obj.get('cause'))
        self.assertIsNotNone(obj.get('data'))

    def test_one_of(self):
        obj = issue('message')
        self.assertIsInstance(obj, Bad)
        self.assertEqual(obj.value.message, 'message')
