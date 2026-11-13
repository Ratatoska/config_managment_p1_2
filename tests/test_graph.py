"""Проверить транзитивность, циклы, глубину и выбор версии."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from apt_index import Requirement, dependency_groups, read_index
from config import load_config
from debian_version import compare
from graph import build_graph
from repository import Package, from_test, pick_release, providers

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"
INDEX = """Package: lib
Version: 1.2

Package: lib
Version: 1.10

Package: provider
Version: 4
Provides: virtual (= 2)
"""


def fixture(name):
    """Загрузить конфигурацию из примеров и построить её граф."""
    config = load_config(EXAMPLES / (name + ".csv"))
    root, neighbors = from_test(config)
    return build_graph(root, neighbors, config.max_depth, config.exclude)


class GraphTests(unittest.TestCase):
    """Проверить графы с разделяемым узлом и циклом."""

    def test_diamond(self):
        """Один узел D имеет два входа, но раскрывается один раз."""
        graph = fixture("diamond")
        self.assertEqual([str(p) for p in graph.edges], list("ABCD"))
        self.assertEqual(graph.edges[Package("C")], (Package("D"),))

    def test_cycle(self):
        """Циклическое ребро сохраняется, обход завершается."""
        graph = fixture("cycle")
        self.assertEqual(graph.edges[Package("C")],
                         (Package("A"), Package("D")))
        self.assertEqual(graph.depth[Package("A")], 0)

    def test_depth_and_filter(self):
        """Граница глубины и исключение отсекают ветви."""
        graph = fixture("filtered")
        self.assertEqual(list(graph.edges), [Package("A"), Package("B")])
        self.assertEqual(graph.edges[Package("B")], ())

    def test_versions_and_provider(self):
        """Числа сравниваются численно, virtual берётся из Provides."""
        packages = read_index(INDEX)
        virtual = providers(packages)
        group = dependency_groups("missing | lib (>= 1.2)")[0]
        self.assertEqual(pick_release(group, packages, virtual).version, "1.10")
        term = Requirement("virtual", ">=", "2")
        self.assertEqual(pick_release((term,), packages, virtual).name,
                         "provider")
        self.assertLess(compare("2.0~rc1", "2.0"), 0)
        self.assertGreater(compare("1:1.0", "9.0"), 0)
