from rich import print
from data import COMMANDS


def prompt():
    print("Welcome to the 8085 emulator.")
    print("Type 'help' for a list of commands.")


def gen_help():
    """
    Generate help text from descriptions of commands
    """
    for cmdname, cmd in COMMANDS.items():
        print(cmdname + " - " + cmd["description"])
