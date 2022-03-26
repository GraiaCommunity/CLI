import os
from typing import (
    Any,
    Callable,
    Deque,
    Generic,
    Iterable,
    List,
    Optional,
    Protocol,
    TypeVar,
)

from prompt_toolkit.filters import is_done
from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import ConditionalContainer, HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.styles import Style

from . import Choice, PromptABC

R = TypeVar("R")


class SupportsIn(Protocol, Generic[R]):
    def __contains__(self, val: R) -> bool:
        ...


class NonNegativeRange:
    def __contains__(self, val: int):
        return val >= 0

    def __str__(self):
        return "range(0, inf)"


class SelectPrompt(PromptABC[List[Choice[R]]]):
    """Select Prompt that supports auto scrolling.
    ```
    [?] Make some choices? (↑ & ↓ : 移动, Space: 选择, Enter: 提交)
    └┬┘ └─────┬──────────┘ └────────────────────┬──────────────────┘
    mark  annotation                           hint
    ❯   ●  A
    ↑ pointer
        ●  B
        ↑ selected
        ○  C
        ↑ unselected
    ```
    """

    def __init__(
        self,
        annotation: str,
        choices: List[Choice[R]],
        mark: str = "[?]",
        pointer: str = "❯",
        selected: str = "●",
        unselected: str = "○",
        hint: str = "(↑ & ↓ : 移动, Space: 选择, Enter: 提交)",
        validator: Optional[Callable[[List[Choice[R]]], bool]] = None,
        range: SupportsIn[int] = NonNegativeRange(),
        overflow_action: Callable[[Deque[int]], Any] = Deque.pop,
        default: Iterable[int] = (),
    ):
        self.annotation: str = annotation
        self.choices: List[Choice[R]] = choices
        self.question_mark: str = mark
        self.pointer: str = pointer
        self.selected: str = selected
        self.unselected: str = unselected
        self.hint: str = hint
        self.validator: Optional[Callable[[List[Choice[R]]], bool]] = validator
        self.cur_index: int = 0
        self.disp_index: int = 0
        self.answered: bool = False
        self.default: Iterable[int] = default
        self.select_deque: Deque[int] = Deque(default)
        self.overflow_action = overflow_action
        self.range = range

    @property
    def max_height(self) -> int:
        return os.get_terminal_size().lines

    def make_layout(self) -> Layout:
        self.answered: bool = False
        self.select_deque: Deque[int] = Deque(self.default)
        return Layout(
            HSplit(
                [
                    Window(
                        FormattedTextControl(self.make_prompt),
                        height=Dimension(1),
                        dont_extend_height=True,
                        always_hide_cursor=True,
                    ),
                    ConditionalContainer(
                        Window(
                            FormattedTextControl(self.make_choice_prompt),
                            height=Dimension(1),
                            dont_extend_height=True,
                        ),
                        ~is_done,
                    ),
                ]
            )
        )

    def make_style(self, style: Style) -> Style:
        default = Style(
            [
                ("mark", "fg:blue"),
                ("annotation", "bold"),
                ("answer", "fg:purple"),
                ("hint", "bold fg:red"),
            ]
        )
        return Style([*default.style_rules, *style.style_rules])

    def make_kb(self) -> KeyBindings:
        kb = KeyBindings()

        @kb.add("up", eager=True)
        def previous(event: KeyPressEvent):
            self.move_up()

        @kb.add("down", eager=True)
        def next(event: KeyPressEvent):
            self.move_down()

        @kb.add("space")
        def select(event: KeyPressEvent):
            if self.cur_index not in self.select_deque:
                self.select_deque.append(self.cur_index)
                while len(self.select_deque) not in self.range:
                    self.overflow_action(self.select_deque)
            else:
                self.select_deque.remove(self.cur_index)

        @kb.add("enter")
        def enter(event: KeyPressEvent):
            if self.validator and not self.validator(self.get_result()):
                return
            self.answered = True
            event.app.exit(result=self.get_result())

        @kb.add("c-c", eager=True)
        def quit(event: KeyPressEvent):
            event.app.exit(result=None)

        return kb

    def make_prompt(self) -> AnyFormattedText:
        prompts: AnyFormattedText = [
            ("class:mark", self.question_mark),
            ("", " "),
            ("class:annotation", self.annotation.strip()),
            ("", " "),
        ]
        if self.answered:
            result = self.get_result()
            prompts.append(
                (
                    "class:answer",
                    ", ".join(choice.name.strip() for choice in result),
                )
            )
        else:
            prompts.append(("class:hint", self.hint))
        return prompts

    def make_choice_prompt(self) -> AnyFormattedText:
        max_num = self.max_height - 1

        prompts: AnyFormattedText = []
        for index, choice in enumerate(self.choices[self.disp_index : self.disp_index + max_num]):
            current_index = index + self.disp_index
            if current_index == self.cur_index:
                prompts.append(("class:pointer", self.pointer))
            else:
                prompts.append(("", " " * len(self.pointer)))
            prompts.append(("", " "))
            if current_index in self.select_deque:
                prompts.append(("class:option", self.selected))
                prompts.append(("", " "))
                prompts.append(("class:option_selected", choice.name.strip() + "\n"))
            else:
                prompts.append(("class:option", self.unselected))
                prompts.append(("", " "))
                prompts.append(("class:option_unselected", choice.name.strip() + "\n"))
        return prompts

    def get_result(self) -> List[Choice[R]]:
        return [self.choices[i] for i in self.select_deque]

    def move_up(self) -> None:
        self.jump((self.cur_index - 1) % len(self.choices))

    def move_down(self) -> None:
        self.jump((self.cur_index + 1) % len(self.choices))

    def jump(self, index: int) -> None:
        self.cur_index = index
        end_index = self.disp_index + self.max_height - 2
        if self.cur_index == self.disp_index and self.disp_index > 0:
            self.disp_index -= 1
        elif self.cur_index == len(self.choices) - 1:
            start_index = len(self.choices) - self.max_height + 1
            self.disp_index = max(start_index, 0)
        elif self.cur_index == end_index and end_index < len(self.choices) - 1:
            self.disp_index += 1
        elif self.cur_index == 0:
            self.disp_index = 0
