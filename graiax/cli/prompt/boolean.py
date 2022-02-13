from typing import Optional

from prompt_toolkit.application import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.enums import DEFAULT_BUFFER
from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.lexers import SimpleLexer
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import Validator

from . import PromptABC

true_pattern = ["y", "yes", "true", "t"]
false_pattern = ["n", "no", "false", "f"]


class BooleanPrompt(PromptABC[bool]):
    """Boolean prompt.

    ```
    [?] Make a choice: (y/n)
    └┬┘ └──────┬─────┘
    mark   annotation
    ```
    """

    def __init__(
        self,
        annotation: str,
        mark: str = "[?]",
        default: Optional[bool] = None,
    ):
        self.annotation: str = annotation
        self.mark: str = mark
        self.default: Optional[bool] = default
        self.buffer: Buffer = None

    def reset(self):
        def bool_validator(input: str) -> bool:
            if not input and self.default is None:
                return False
            elif input and input.lower() not in true_pattern + false_pattern:
                return False
            return True

        def submit(buffer: Buffer) -> bool:
            input = buffer.document.text
            if not input:
                buffer.document.insert_after(str(self.default))
                get_app().exit(result=self.default)
            elif input.lower() in true_pattern:
                get_app().exit(result=True)
            else:
                get_app().exit(result=False)
            return True

        self.buffer: Buffer = Buffer(
            validator=Validator.from_callable(bool_validator),
            name=DEFAULT_BUFFER,
            accept_handler=submit,
        )

    def make_layout(self) -> Layout:
        self.reset()
        layout = Layout(
            HSplit(
                [
                    Window(
                        BufferControl(self.buffer, lexer=SimpleLexer("class:answer")),
                        get_line_prefix=self.make_prompt,
                    )
                ]
            )
        )
        return layout

    def make_style(self, style: Style) -> Style:
        default = Style(
            [
                ("mark", "fg:blue"),
                ("annotation", "bold"),
                ("choice", "bold fg:blue"),
                ("answer", "fg:green"),
            ]
        )
        return Style([*default.style_rules, *style.style_rules])

    def make_kb(self) -> KeyBindings:
        kb = KeyBindings()

        @kb.add("enter", eager=True)
        def enter(event: KeyPressEvent):
            self.buffer.validate_and_handle()

        @kb.add("c-c", eager=True)
        def quit(event: KeyPressEvent):
            event.app.exit(result=None)

        return kb

    def make_prompt(self, line_number: int, wrap_count: int) -> AnyFormattedText:
        prompt = [
            ("class:mark", self.mark),
            ("", " "),
            ("class:annotation", self.annotation.strip()),
            ("", " "),
        ]
        if self.default:
            prompt.append(("class:choice", "(Y/n)"))
        elif self.default == False:
            prompt.append(("class:choice", "(y/N)"))
        else:
            prompt.append(("class:choice", "(y/n)"))
        prompt.append(("", " "))
        return prompt
