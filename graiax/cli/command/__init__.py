import os
from typing import List

commands: List[str] = [
    file[:-3]
    for file in os.listdir(os.path.dirname(__file__))
    if file.endswith(".py") and not file.startswith("_")
]
