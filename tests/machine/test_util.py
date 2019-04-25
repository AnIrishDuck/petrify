import unittest

from petrify.machine.util import frange

class TestUtil(unittest.TestCase):
    def test_frange_inclusive(self):
        self.assertEqual(
            list(frange(-1, -5, -1, inclusive=True)),
            [-1, -2, -3, -4, -5]
        )
