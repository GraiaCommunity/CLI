import os
import pkgutil
from pathlib import Path

import tomlkit
from tomlkit.items import Array, Table

from ..prompt.export import FChoice, SelectPrompt
from ..util import pprint


def scan_modules(seg: list[str], path: str) -> set[str]:
    """扫描指定目录下的所有模块"""
    modules = []
    for _, name, is_pkg in pkgutil.iter_modules([path]):
        if is_pkg:
            modules.extend(".".join([name, mod]) for mod in scan_modules(seg + [name], f"{path}/{name}"))
        modules.append(name)
    return modules


def inject(args):
    """向已有项目的 pyproject.toml 注入数据"""
    pyproject_path = Path(os.getcwd()).joinpath("pyproject.toml")
    pprint("<b><cyan>向 pyproject.toml 注入数据...</cyan></b> ")
    data = tomlkit.loads(pyproject_path.read_text(encoding="utf-8"))
    tool_table: Table = data.setdefault("tool", tomlkit.table(True))
    graiax_table: Table = tool_table.setdefault("graiax", tomlkit.table())
    loader_array: Array = graiax_table.setdefault("load", tomlkit.array())
    loader_array.comment("modules which will be loaded by graia-saya")
    possible_mods = scan_modules([], ".")
    modules = SelectPrompt("选择运行时要加载的模块", choices=[FChoice(mod) for mod in possible_mods]).prompt()
    if modules is None:
        pprint("<b><red>! 取消操作 !</red></b>")
        return
    for mod in modules:
        loader_array.add_line(mod.data)
    loader_array.add_line(indent="")
    with open(pyproject_path, "w", encoding="utf-8") as f:
        tomlkit.dump(data, f)
    pprint("<b><green>数据写入完毕！</green></b>")
