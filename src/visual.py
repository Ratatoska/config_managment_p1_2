"""Сформировать PlantUML и сохранить SVG через локальный рендерер."""

import os
from pathlib import Path
import re
import subprocess
from xml.etree import ElementTree

SVG_TAG = "{http://www.w3.org/2000/svg}svg"
RENDER_TIMEOUT = 60


def plantuml(graph):
    """Выдать описание узлов и рёбер с короткими уникальными псевдонимами."""
    aliases = {node: f"p{i}" for i, node in enumerate(graph.edges)}
    lines = ["@startuml", "left to right direction",
             "skinparam componentStyle rectangle"]
    for node, alias in aliases.items():
        label = re.sub(r"[^A-Za-z0-9 ._:+~()=|\-]", " ", str(node))
        lines.append(f'component "{label}" as {alias}')
    for node, children in graph.edges.items():
        lines.extend(f"{aliases[node]} --> {aliases[child]}"
                     for child in children)
    return "\n".join([*lines, "@enduml", ""])


def render_svg(graph, output):
    """Создать рядом .puml и передать его PlantUML через стандартный ввод."""
    jar = Path(os.environ.get("PLANTUML_JAR", "plantuml.jar")).resolve()
    if not jar.is_file():
        raise ValueError("Укажите путь к plantuml.jar в PLANTUML_JAR")
    source = plantuml(graph)
    command = ["java", "-DPLANTUML_SECURITY_PROFILE=SANDBOX", "-jar",
               jar.name, "-charset", "UTF-8", "-tsvg", "-pipe"]
    result = subprocess.run(
        command, cwd=jar.parent, input=source.encode("utf-8"),
        capture_output=True, timeout=RENDER_TIMEOUT, check=False,
    )
    if result.returncode:
        message = result.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(f"PlantUML не смог построить SVG: {message}")
    if ElementTree.fromstring(result.stdout).tag != SVG_TAG:
        raise ValueError("PlantUML вернул данные не в формате SVG")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.with_suffix(".puml").write_text(source, encoding="utf-8")
    output.write_bytes(result.stdout)
