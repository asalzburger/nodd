"""Adverse scientific-interval rendering check."""
import unittest
import plot
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np


class IntervalPlotTest(unittest.TestCase):
    def test_percentile_interval_outside_point_keeps_actual_endpoints(self):
        fig, ax = plt.subplots()
        try:
            plot.points(ax, [1.], [95.], 1., [[100., 110.]])
            bars = [item for item in ax.collections if isinstance(item, LineCollection)]
            self.assertEqual(len(bars), 1)
            np.testing.assert_array_equal(bars[0].get_segments()[0], [[1., 100.], [1., 110.]])
        finally:
            plt.close(fig)


if __name__ == "__main__":
    unittest.main()
