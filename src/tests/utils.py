def compare_values(test_case, items):
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
        a, b, *msg = item
        test_case.assertEqual(a, b, msg and msg[0] or None)
