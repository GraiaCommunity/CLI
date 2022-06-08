import argparse
import importlib

from . import command


def main():
    # load commands
    parser = argparse.ArgumentParser(description="GraiaCommunity CLI")

    sub = parser.add_subparsers(help="子命令帮助")

    sub_parsers = {}

    for cmd in command.commands:
        module = importlib.import_module(f"{command.__package__}.{cmd}")
        func = getattr(module, cmd)
        sub_parsers[cmd] = sub.add_parser(cmd, help=func.__doc__)
        sub_parsers[cmd].set_defaults(func=func)

    args = parser.parse_args()
    if "func" in args:
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
