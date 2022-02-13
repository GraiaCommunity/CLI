from . import Choice, Result_T
from .boolean import BooleanPrompt
from .select import SelectPrompt
from .text import TextPrompt


class FChoice(Choice[Result_T]):
    def __init__(self, value: Result_T):
        self.name = str(value)
        self.data = value
