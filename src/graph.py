"""Построение графа рекурсивным обходом в ширину."""

from dataclasses import dataclass


@dataclass
class Graph:
    """Список рёбер и минимальное расстояние до каждого узла."""

    edges: dict
    depth: dict


def build_graph(root, neighbors, max_depth, exclude=""):
    """Раскрыть один уровень BFS, затем рекурсивно перейти к следующему."""
    graph = Graph({root: ()}, {root: 0})

    def visit_level(frontier, depth):
        """Обработать текущий слой и собрать ещё не посещённые узлы."""
        if not frontier or depth == max_depth:
            return
        upcoming = []
        for node in frontier:
            children = tuple(child for child in neighbors(node)
                             if not exclude or exclude not in child.name)
            graph.edges[node] = children
            for child in children:
                if child not in graph.depth:
                    graph.depth[child] = depth + 1
                    graph.edges[child] = ()
                    upcoming.append(child)
        visit_level(upcoming, depth + 1)

    visit_level([root], 0)
    return graph


def print_graph(graph):
    """Показать рёбра в порядке обхода и отметки о границе глубины."""
    for node, children in graph.edges.items():
        targets = ", ".join(map(str, children)) or "—"
        print(f"[{graph.depth[node]}] {node} -> {targets}")
