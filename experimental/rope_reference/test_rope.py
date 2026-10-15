import math
import unittest

from experimental.rope_reference.rope import dot, rotate


class RopeTests(unittest.TestCase):
    def test_zero_position_identity(self):
        x = (1.0, 2.0, 3.0, 4.0)
        self.assertEqual(rotate(x, 0), x)

    def test_norm_is_preserved(self):
        x = (1.0, -2.0, 3.0, 4.0)
        self.assertAlmostEqual(dot(rotate(x, 100), rotate(x, 100)), dot(x, x))

    def test_relative_position_invariance(self):
        q, k = (0.3, 0.5, 0.7, -0.2), (0.2, 0.4, -0.1, 0.6)
        self.assertAlmostEqual(dot(rotate(q, 4), rotate(k, 9)),
                               dot(rotate(q, 104), rotate(k, 109)), places=11)

    def test_invalid_inputs(self):
        for vector, position in (((), 0), ((1.0,), 1), ((math.nan, 1.0), 1), ((1.0, 2.0), -1)):
            with self.assertRaises(ValueError):
                rotate(vector, position)


if __name__ == "__main__":
    unittest.main()
