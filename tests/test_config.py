"""Проверки ошибок всех семи параметров CSV."""

from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from config import load_config


class ConfigTests(unittest.TestCase):
    """Проверить корректный CSV и некорректные настройки."""

    def prepare(self):
        """Подготовить временные входные данные."""
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "config.csv"
        self.path.with_name("graph.txt").write_text("A:\n", encoding="utf-8")
        self.rows = {"package": "A", "repository": "graph.txt",
                     "test_mode": "true", "version": "1.0",
                     "output": "result.svg", "max_depth": "3", "exclude": ""}

    def load(self):
        """Записать текущие настройки и загрузить их."""
        self.path.write_text(
            "".join(f"{k},{v}\n" for k, v in self.rows.items()),
            encoding="utf-8",
        )
        return load_config(self.path)

    def test_valid_config(self):
        """Пути в CSV интерпретируются относительно самого CSV."""
        self.prepare()
        config = self.load()
        self.assertEqual(config.package, "A")
        self.assertTrue(Path(config.repository).is_file())
        self.assertEqual(config.output.parent, self.path.parent)

    def test_invalid_fields(self):
        """Каждый ошибочный параметр даёт сообщение с его именем."""
        self.prepare()
        wrong = {"package": "a", "repository": "missing.txt",
                 "test_mode": "maybe", "version": "latest",
                 "output": "result.txt", "max_depth": "-1", "exclude": "!"}
        for key, value in wrong.items():
            with self.subTest(key=key):
                previous = self.rows[key]
                self.rows[key] = value
                with self.assertRaisesRegex(ValueError, key):
                    self.load()
                self.rows[key] = previous

    def test_missing_field(self):
        """Отсутствующий ключ диагностируется."""
        self.prepare()
        del self.rows["version"]
        with self.assertRaisesRegex(ValueError, "version"):
            self.load()
