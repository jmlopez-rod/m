import unittest
from m.core import one_of
from m.core.fp import Bad, Good
from ..util import compare_values


class OneOfTest(unittest.TestCase):
    def test_instances(self):
        left, right = [Bad(False), Good(1)]
        compare_values(self, [
            [left.is_bad, True, '"left" should be Bad(False)'],
            [right.is_bad, False, '"right" should be Good(1)'],
        ])

    def test_iteration(self):
        self.assertListEqual(list(Bad('err').iter()), [])
        self.assertListEqual(list(Good(100).iter()), [100])
        bad = one_of(lambda x: x)
        left = one_of(lambda: list(Bad('error')))
        right = one_of(lambda: list(Good(99)))
        self.assertIsInstance(bad, Bad)
        self.assertIsInstance(left, Bad)
        self.assertIsInstance(right, Good)
        self.assertEqual(left.value, 'error')
        self.assertEqual(right.value, 99)
