import os
import subprocess
from collections import deque
from pathlib import Path

import tomlkit
import typer
from prompt_toolkit import HTML, print_formatted_text

from graiax.cli.prompt import Choice

from ..prompt.export import BooleanPrompt, FChoice, SelectPrompt


def pprint(text: str):
    print_formatted_text(HTML(text))


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
    full = BooleanPrompt("是否使用 graia-ariadne 的完整版本 (包含 Scheduler 与 Alconna)？", default=True).prompt(
        default=True
    )
    subprocess.run(
        [
            "pdm",
            "add",
            f"graia-ariadne{'[full]' if full else ''}",
        ]
        + (["graia-saya"] if not full else [])
        + ["--no-sync", "--save-compatible"]
    )
    format_tools = BooleanPrompt("是否添加 black 与 isort 到开发依赖？", default=True).prompt(default=True)
    if format_tools:
        subprocess.run(["pdm", "add", "-d", "black", "isort", "--no-sync", "--save-compatible"])
    install = BooleanPrompt("现在安装依赖？你之后可以通过 pdm install 来手动安装").prompt()
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
    # add mirror
    mirrors = SelectPrompt("添加哪些 PyPI 镜像？", choices=pypi_mirrors, default=[pypi_mirrors[0]]).prompt(
        default=[pypi_mirrors[0]]
    )
    if mirrors:
        source_aot = tomlkit.aot()
        for index, mirror in enumerate(mirrors):
            source_aot.append(tomlkit.item({"name": mirror.name, "url": mirror.data, "default": not index}))
        data["tool"]["poetry"].append("source", source_aot)

    Path(os.getcwd()).joinpath("pyproject.toml").write_text(tomlkit.dumps(data), encoding="utf-8")
    pprint("<green>添加依赖...</green>")
    full = BooleanPrompt("是否使用 graia-ariadne 的完整版本 (包含 Scheduler 与 Alconna)？", default=True).prompt(
        default=True
    )
    subprocess.run(
        ["poetry", "add", "graia-ariadne"]
        + (["-E", "full"] if full else ["graia-saya"])
        + [
            "--lock",
            "--ansi",
        ]
    )
    format_tools = BooleanPrompt("是否添加 black 与 isort 到开发依赖？", default=True).prompt(default=True)
    if format_tools:
        subprocess.run(["poetry", "add", "--dev", "black", "isort", "--lock", "--ansi"])
    install = BooleanPrompt("现在安装依赖？你之后可以通过 poetry install 来手动安装").prompt()
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
        [FChoice("poetry"), FChoice("pdm"), FChoice("pip")],
        validator=lambda x: len(x) == 1,
        range=(0, 1),
        overflow_action=deque.popleft,
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
        globals()[manager]()
    except KeyboardInterrupt:
        pprint("<b><red>! 终止操作 !</red></b>")
        return
    # pprint("<b>INFO</b>: 创建项目文件")
    # create_structure()
    # TODO: create structure
