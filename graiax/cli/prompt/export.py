from . import Choice, Result_T
from .boolean import BooleanPrompt as BooleanPrompt
from .select import SelectPrompt as SelectPrompt
from .text import TextPrompt as TextPrompt


class FChoice(Choice[Result_T]):
    def __init__(self, value: Result_T):
        self.name = str(value)
        self.data = value
