from prompt_toolkit import HTML, print_formatted_text


def pprint(text: str, end: str = "\n"):
    print_formatted_text(HTML(text), end=end)
