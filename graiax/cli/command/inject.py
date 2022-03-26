import os
from pathlib import Path

import tomlkit
from tomlkit.container import Container
from tomlkit.items import Table, Trivia
from typer import Typer

from ..util import pprint

app = Typer()


def inject():
    pyproject_path = Path(os.getcwd()).joinpath("pyproject.toml")
    pprint("<b><cyan>向 pyproject.toml 注入数据...</cyan></b> ")
    data = tomlkit.loads(pyproject_path.read_text(encoding="utf-8"))
    tool_table: Table = data.setdefault("tool", tomlkit.table(True))
    graiax_table: Table = tool_table.setdefault("graiax", tomlkit.table())
    loader_table: Table = graiax_table.setdefault(
        "loader", Table(Container(), Trivia(comment_ws="  ", comment="# Saya 会加载的模块"), False, False)
    )
    with open(pyproject_path, "w", encoding="utf-8") as f:
        tomlkit.dump(data, f)
    pprint("<b><green>数据写入完毕！</green></b>")


app.command()(inject)
