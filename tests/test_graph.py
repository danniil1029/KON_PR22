"""Проверки обхода в ширину на тестовом репозитории."""

import unittest
from pathlib import Path

from src.graph import build_graph, read_test_graph
from src.nuget import Package

FIXTURE = Path(__file__).parent / "fixtures" / "graph.json"
ROOT = Package("A")


class GraphTests(unittest.TestCase):
    """Проверить порядок, цикл, ограничения и изолированный узел."""

    def test_cycle_and_shared_dependency(self):
        """Сохранить все связи, но раскрыть каждый узел один раз."""
        source = read_test_graph(FIXTURE)
        seen = []

        def dependencies(package):
            """Запомнить фактический порядок посещения."""
            seen.append(package.name)
            return source[package]

        graph = build_graph(ROOT, dependencies)
        self.assertEqual(seen, ["A", "B", "C", "D", "EXTRA", "E"])
        self.assertEqual(graph[Package("D")], [ROOT])
        self.assertIn(Package("D"), graph[Package("B")])
        self.assertIn(Package("D"), graph[Package("C")])

    def test_max_depth(self):
        """Показать узлы предельного уровня без их потомков."""
        source = read_test_graph(FIXTURE)
        graph = build_graph(ROOT, source.__getitem__, max_depth=1)
        self.assertEqual(list(graph), list(map(Package, "ABC")))
        self.assertEqual(graph[Package("B")], [])
        self.assertEqual(graph[Package("C")], [])

    def test_exclusion(self):
        """Исключить ветку, доступную только через отфильтрованный узел."""
        source = read_test_graph(FIXTURE)
        graph = build_graph(ROOT, source.__getitem__, exclude="ext")
        self.assertNotIn(Package("EXTRA"), graph)
        self.assertNotIn(Package("E"), graph)
        self.assertEqual(graph[Package("C")], [Package("D")])

    def test_isolated_package(self):
        """Вернуть граф из одного узла для пакета без зависимостей."""
        source = read_test_graph(FIXTURE)
        package = Package("F")
        self.assertEqual(build_graph(package, source.__getitem__),
                         {package: []})
