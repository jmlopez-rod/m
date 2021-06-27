from typing import List, Any


def compare_values(test_case, items: List[Any]) -> None:
    """Compare multiple values without callng assertEqual
    on each line.

        self.assertEqual(a, 1)
        self.assertEqual(b, 2, 'message')

    same as

        compare_values(self, [
            [a, 1],
            [b, 2, 'message'],
        ])

    """
    for item in items:
        x, y, *msg = item
        test_case.assertEqual(x, y, msg and msg[0] or None)
