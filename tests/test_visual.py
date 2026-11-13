"""Проверки текста PlantUML и запуска рендерера, если он настроен."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from xml.etree import ElementTree

from test_graph import fixture
from visual import SVG_TAG, plantuml, render_svg


class VisualTests(unittest.TestCase):
    """Проверить все рёбра, включая разделяемый узел и цикл."""

    def test_diamond_edges(self):
        """Граф из четырёх узлов сохраняет оба входа в D."""
        source = plantuml(fixture("diamond"))
        self.assertTrue(source.startswith("@startuml\n"))
        self.assertIn('component "D" as p3', source)
        self.assertIn("p1 --> p3", source)
        self.assertIn("p2 --> p3", source)

    def test_cycle_edge(self):
        """Циклическое ребро не теряется при визуализации."""
        self.assertIn("p2 --> p0", plantuml(fixture("cycle")))

    @unittest.skipUnless(os.environ.get("PLANTUML_JAR"), "set PLANTUML_JAR")
    def test_svg_file(self):
        """Проверить настоящий SVG и сохранение исходника PlantUML."""
        with TemporaryDirectory() as folder:
            output = Path(folder) / "nested" / "graph.svg"
            render_svg(fixture("diamond"), output)
            self.assertEqual(ElementTree.parse(output).getroot().tag, SVG_TAG)
            self.assertIn("p2 --> p3", output.with_suffix(".puml").read_text())
