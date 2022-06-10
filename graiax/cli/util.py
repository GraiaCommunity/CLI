import pkgutil

from prompt_toolkit import HTML, print_formatted_text


def pprint(text: str, end: str = "\n"):
    print_formatted_text(HTML(text), end=end)


def scan_modules(seg: list[str], path: str) -> set[str]:
    """扫描指定目录下的所有模块"""
    modules = []
    for _, name, is_pkg in pkgutil.iter_modules([path]):
        if is_pkg:
            modules.extend(".".join([name, mod]) for mod in scan_modules(seg + [name], f"{path}/{name}"))
        modules.append(name)
    return modules


def snake_to_camel(name: str) -> str:
    """将 snake_case 字符串转换为 CamelCase 字符串"""
    return "".join(map(lambda x: x.capitalize(), name.split("_")))
