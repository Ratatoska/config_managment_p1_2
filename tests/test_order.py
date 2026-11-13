"""Проверить порядок для ромба, цикла и ограничения глубины."""

import unittest

from test_graph import fixture
from load_order import load_order


class OrderTests(unittest.TestCase):
    """Проверки порядка вывода и диагностики циклов."""

    def test_dependencies_before_parents(self):
        """Общий D идёт перед B и C и выводится один раз."""
        result = load_order(fixture('diamond'))
        self.assertEqual([str(p) for p in result.packages], list('DBCA'))
        self.assertEqual(result.cycles, [])

    def test_reports_cycle(self):
        """В цикле строгого порядка нет, но все узлы выводятся."""
        result = load_order(fixture('cycle'))
        self.assertEqual([str(p) for p in result.cycles[0]], list('ABCA'))
        self.assertEqual([str(p) for p in result.packages], list('DCBA'))

    def test_filtered_order(self):
        """Порядок учитывает только вершины проанализированного графа."""
        result = load_order(fixture('filtered'))
        self.assertEqual([str(p) for p in result.packages], list('BA'))
