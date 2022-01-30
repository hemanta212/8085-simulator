"""
An 8085 interpreter written in Python.
"""
import sys
from loguru import logger

from command_model import Command
from state_model import State
from data import REGISTERS, COMMANDS


def prompt():
    print("Welcome to the 8085 emulator.")
    print("Type 'help' for a list of commands.")


def gen_help():
    """
    Generate help text from descriptions of commands
    """
    for cmdname, cmd in COMMANDS.items():
        print(cmdname + " - " + cmd["description"])


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
            elif cmd is None:
                print("Unknown command.")


def cmd_processor(cmd, state):
    """
    Return a Command object.
    """
    args = cmd.split(" ")
    cmdname = args[0]
    cmdargs = args[1:]
    process_hex(cmdargs)
    if cmdname in COMMANDS:
        logger.debug(f"Command {cmdname} found.")
        return Command(cmdname, cmdargs, state)
    else:
        return None

def process_hex(cmdargs):
    """
    Convert hex strings to ints.
    """
    for arg in cmdargs:
        hex_code = arg
        if arg in REGISTERS:
            continue

        if arg[-1].lower() == "h":
            hex_code = "0x" + arg[:-1]
        else:
            hex_code = "0x" + arg

        logger.debug(f"{int(hex_code, 16)} == {int(hex(int(hex_code, 16)), 16)}")
        if int(hex_code, 16) == int(hex(int(hex_code, 16)), 16):
            cmdargs[cmdargs.index(arg)] = hex_code
        else:
            logger.warning(f"Invalid token: {arg}")
            continue
        

if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stderr, level="DEBUG")
#    logger.disable("__main__")
    main()
