import os
from typing import List

commands: List[str] = []
for file in os.listdir(os.path.dirname(__file__)):
    if file.endswith(".py") and not file.startswith("_"):
        commands.append(file[:-3])
