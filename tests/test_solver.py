import unittest
from petrify import solid
from petrify.solver import solve_matrix

class TestSolver(unittest.TestCase):
    def test_simple(self):
        solution = solve_matrix([
            [0, 1, -1, -2],
            [1, 1, 1, 13],
            [1, -2, 0, 3],
        ])
        self.assertEqual(solution, [7, 2, 4])
