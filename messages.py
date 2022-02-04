from rich import print
from data import COMMANDS


def msg_welcome():
    print("Welcome to the 8085 emulator.")
    print("Type 'help' for a list of commands.")


def msg_help():
    """
    Generate help text from descriptions of commands
    """
    for cmdname, cmd in COMMANDS.items():
        print(cmdname + " - " + cmd["description"])


def msg_cli_help():
    """
    Generate help text when run hep option from cli
    """
    options = [
        ":8085 Interpreter:\n",
        "help | --help | -h : Display this message",
        "-i                 : Run in indirect mode, dont display welcome msg and >>> prompt",
        "-db <FILENAME>     : Run in file db mode save and restore after each cmd from file",
        "-f <FILENAME>      : Read command/commands from file",
        '-c "cmd1;cmd2"     : Run cmd directly, separate with ";" for more than one commands',
        "\nNOTE: In case of using multiple options, they need to be specified in order listed above.",
    ]
    msg = "\t\n".join(options)
    print(msg)
