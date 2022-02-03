"""
An 8085 interpreter written in Python.
"""
import sys
from loguru import logger
from rich import print

from command_model import Command
from state_model import State
from data import COMMANDS
from messages import prompt, gen_help
from converter import process_hex


def main():
    prompt()
    state = State()
    while True:
        command = input(">>> ")
        logger.debug(f"Command received: {command}")
        if command == "help":
            gen_help()
        elif command == "quit":
            break
        elif command == "inspect":
            state.inspect()
        else:
            cmd = cmd_processor(command, state)
            if cmd is not None and cmd.is_valid:
                cmd.eval()


def cmd_processor(cmd: str, state: State) -> Command:
    """
    Return a Command object.
    """
    cmd_list = tuple(cmd.split(" "))
    first, second = 0, 1
    cmdname, cmdargs = cmd_list[first], cmd_list[second:]
    p_cmdargs = process_hex(cmdargs)
    if cmdname not in COMMANDS:
        logger.error(f"Command {cmdname} found.")
        return None
    elif cmdargs and not p_cmdargs:
        return None
    else:
        logger.debug(f"Command {cmdname} found.")
        return Command(cmdname, p_cmdargs, state)


if __name__ == "__main__":
    logger.remove()
    logger.add("debug.log", level="DEBUG", rotation="1 MB")
    logger.add(sys.stderr, level="WARNING")
    main()
