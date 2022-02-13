import importlib
from typing import Protocol

import typer

from . import command

app: typer.Typer = typer.Typer()


class HasTyperApp(Protocol):
    @property
    def app(self) -> typer.Typer:
        ...


@app.callback()
def finish():
    """Finish up and cleanup log."""


def main():
    # load commands

    for cmd in command.commands:
        module: HasTyperApp = importlib.import_module(f"{command.__package__}.{cmd}")
        app.registered_commands += module.app.registered_commands

    app()


if __name__ == "__main__":
    main()
