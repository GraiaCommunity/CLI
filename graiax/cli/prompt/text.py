from typing import Callable, Optional

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


class TextPrompt(PromptABC[str]):
    """Simple text input prompt.

    ```
    [?] Reply to the question: answer
    └┬┘ └─────────┬──────────┘ └──┬─┘
    mark      annotation       answer
    ```
    """

    def __init__(
        self,
        annotation: str,
        mark: str = "[?]",
        validator: Optional[Callable[[str], bool]] = None,
    ):
        self.annotation: str = annotation
        self.mark: str = mark
        self.validator: Optional[Callable[[str], bool]] = validator
        self.buffer: Buffer = None

    def reset(self):
        def submit(buffer: Buffer) -> bool:
            get_app().exit(result=buffer.document.text)
            return True

        self.buffer: Buffer = Buffer(
            name=DEFAULT_BUFFER,
            validator=Validator.from_callable(self.validator) if self.validator else None,
            accept_handler=submit,
        )

    def make_layout(self) -> Layout:
        self.reset()
        layout = Layout(
            HSplit(
                [
                    Window(
                        BufferControl(self.buffer, lexer=SimpleLexer("class:answer")),
                        get_line_prefix=self.make_ft,
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

    def make_ft(self, *_: int) -> AnyFormattedText:
        return [
            ("class:mark", self.mark),
            ("", " "),
            ("class:annotation", self.annotation.strip()),
            ("", " "),
        ]
