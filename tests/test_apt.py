"""Проверки чтения зависимостей и выбора точной версии."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from apt_index import exact_release, read_index

INDEX = """Package: hello
Version: 1.0
Pre-Depends: core
Depends: lib (>= 2), extra:any | other,
 support
Description: test
 second line

Package: hello
Version: 2.0
Depends: newest
"""


class AptTests(unittest.TestCase):
    """Разбор настоящего формата индекса Packages."""

    def test_exact_release_and_dependencies(self):
        """Pre-Depends, ограничения, альтернативы и переносы сохраняются."""
        release = exact_release(read_index(INDEX), "hello", "1.0")
        display = [[str(term) for term in group] for group in release.groups]
        self.assertEqual(display, [
            ["core"], ["lib (>= 2)"], ["extra", "other"], ["support"],
        ])

    def test_missing_version(self):
        """При неизвестной версии программа показывает доступные."""
        with self.assertRaisesRegex(ValueError, "доступны 1.0, 2.0"):
            exact_release(read_index(INDEX), "hello", "3.0")
