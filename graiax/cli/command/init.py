import os
import subprocess
from collections import deque
from pathlib import Path

import tomlkit
import typer

from graiax.cli.prompt import Choice

from ..prompt.export import BooleanPrompt, FChoice, SelectPrompt
from ..util import pprint

extras_intro = """<b><cyan>\
Scheduler: 任务计划器
Alconna: 复杂但强大的命令解析器
FastAPI: 用于提供反向适配器后端</cyan></b>
"""

extra_prompt = SelectPrompt(
    "添加额外依赖？",
    choices=[
        Choice("[graia]: 包括 Scheduler", "graia"),
        Choice("[standard]: 包括 Scheduler, Alconna", "standard"),
        Choice("[full]: 包括 Scheduler, Alconna, FastAPI", "full"),
    ],
    default=[0],
    validator=lambda x: len(x) <= 1,
    range=(0, 1),
    overflow_action=deque.popleft,
)

app = typer.Typer()


def toml_exist():
    path = Path(os.getcwd()).joinpath("pyproject.toml")
    return path.exists()


def create_structure():
    ...


def pdm():
    subprocess.run(["pdm", "init", "-n"])
    data = tomlkit.loads(Path(os.getcwd()).joinpath("pyproject.toml").read_text())
    project = data["project"]
    project["license"]["text"] = "AGPL-3.0"  # modify license
    Path(os.getcwd()).joinpath("pyproject.toml").write_text(tomlkit.dumps(data))
    pprint("<green>添加依赖...</green>")
    pprint(extras_intro, "")
    extra = extra_prompt.prompt()
    subprocess.run(
        (
            (
                [
                    "pdm",
                    "add",
                    f"graia-ariadne{f'[{extra[0].data}]' if extra else ''}",
                ]
                + ([] if extra else ["graia-saya"])
            )
            + ["--no-sync", "--save-compatible"]
        )
    )

    format_tools = BooleanPrompt("是否添加 black 与 isort 到开发依赖？", default=True).prompt(default=True)
    if format_tools:
        subprocess.run(["pdm", "add", "-d", "black", "isort", "--no-sync", "--save-compatible"])
    install = BooleanPrompt("现在安装依赖？你之后可以通过 pdm install 来手动安装", default=True).prompt(default=True)
    if install:
        subprocess.run(["pdm", "install"])


pypi_mirrors = [
    Choice("aliyun", "https://mirrors.aliyun.com/pypi/simple"),
    Choice("tuna-tsinghua", "https://pypi.tuna.tsinghua.edu.cn/simple"),
]


def poetry():
    subprocess.run(["poetry", "init", "--ansi", "-n", "--quiet"])
    data = tomlkit.loads(Path(os.getcwd()).joinpath("pyproject.toml").read_text())
    data["tool"]["poetry"].update({"license": "AGPL-3.0"})  # modify license
    if mirrors := SelectPrompt("添加哪些 PyPI 镜像？", choices=pypi_mirrors, default=[0]).prompt(
        default=[pypi_mirrors[0]]
    ):
        source_aot = tomlkit.aot()
        for index, mirror in enumerate(mirrors):
            source_aot.append(tomlkit.item({"name": mirror.name, "url": mirror.data, "default": not index}))
        data["tool"]["poetry"].append("source", source_aot)

    Path(os.getcwd()).joinpath("pyproject.toml").write_text(tomlkit.dumps(data), encoding="utf-8")
    pprint("<green>添加依赖...</green>")
    pprint(extras_intro, "")
    extra = extra_prompt.prompt()
    subprocess.run(
        ["poetry", "add", "graia-ariadne"]
        + (["-E", extra[0].data] if extra else ["graia-saya"])
        + [
            "--lock",
            "--ansi",
        ]
    )
    format_tools = BooleanPrompt("是否添加 black 与 isort 到开发依赖？", default=True).prompt(default=True)
    if format_tools:
        subprocess.run(["poetry", "add", "--dev", "black", "isort", "--lock", "--ansi"])
    install = BooleanPrompt("现在安装依赖？你之后可以通过 poetry install 来手动安装", default=True).prompt(default=True)
    if install:
        subprocess.run(["poetry", "install", "--ansi"])


def pip():
    # no support
    pprint("<yellow>我们建议不使用 <magenta>pip</magenta> 来管理项目与依赖项.</yellow>")
    pprint("<yellow>请换用 <magenta>poetry</magenta> 或 <magenta>pdm</magenta> 管理</yellow>")
    raise KeyboardInterrupt  # exit


@app.command()
def init():
    pprint("<b><green>使用 Graia 脚手架创建项目...</green></b>")
    choices = SelectPrompt(
        "请选择新项目的包管理器",
        [FChoice("pip"), FChoice("poetry"), FChoice("pdm")],
        validator=lambda x: len(x) == 1,
        range=(0, 1),
        overflow_action=deque.popleft,
        default=[0],
    ).prompt()
    if not choices:
        pprint("<b><red>! 用户终止操作</red></b>")
        return
    (choice,) = choices
    manager: str = choice.data
    pprint("<b>INFO</b>: 验证包管理器存在")
    try:
        subprocess.run([manager, "--version"])
    except FileNotFoundError:
        pprint(f"<b><red>! 没有找到 <magenta>{manager}</magenta> 包管理器</red></b>")
        pprint("<b><red>! 操作中止 !</red></b>")
        return
    if not toml_exist():
        pprint("<yellow>检测到 pyproject.toml 不存在...</yellow>")
    try:
        pprint(f"<b>INFO</b>: 使用 <magenta>{manager}</magenta> 创建项目元数据")
        print()
        globals()[manager]()
        print()
    except KeyboardInterrupt:
        pprint("<b><red>! 终止操作 !</red></b>")
        return

    from . import inject

    inject.inject()
