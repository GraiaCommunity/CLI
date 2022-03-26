"""Prompt interaction module.
Thanks to the nb-cli project for providing base schemes."""
import abc
from dataclasses import dataclass
from typing import Generic, Optional, TypeVar, Union

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.styles import Style

Default_T = TypeVar("Default_T")
Result_T = TypeVar("Result_T")


class PromptABC(abc.ABC, Generic[Result_T]):
    @abc.abstractmethod
    def make_layout(self) -> Layout:
        raise NotImplementedError

    @abc.abstractmethod
    def make_style(self, style: Style) -> Style:
        raise NotImplementedError

    @abc.abstractmethod
    def make_kb(self) -> KeyBindings:
        raise NotImplementedError

    def build_app(self, style: Style) -> Application:
        return Application(
            layout=self.make_layout(),
            style=self.make_style(style),
            key_bindings=self.make_kb(),
            mouse_support=True,
        )

    def prompt(
        self,
        default: Default_T = None,
        style: Optional[Style] = None,
    ) -> Union[Default_T, Result_T]:
        print()
        app = self.build_app(style or Style([]))
        result: Result_T = app.run()
        print()
        if result is None:
            return default
        return result


@dataclass
class Choice(Generic[Result_T]):
    name: str
    data: Result_T = None
