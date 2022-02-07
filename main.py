"""
An 8085 interpreter written in Python.
"""
import sys
import readline
from typing import Optional

from loguru import logger

from command_model import Command
from state_model import State
from interpreter import Interpreter
from data import COMMANDS
from messages import msg_welcome, msg_help
from converter import (
    process_instruction_args,
    is_label,
    process_cmd_line_args,
    process_comments,
)


def main(commands: tuple = tuple(), file_db: str = "", indirect_mode: bool = False):
    interpreter = Interpreter()
    for command in commands:
        process_command(command, interpreter, file_db)

    if not commands:
        if not indirect_mode:
            msg_welcome()
        while True:
            try:
                command = input(">>> ") if not indirect_mode else input("")
                process_command(command, interpreter, file_db)
                readline.add_history(command)
            except EOFError:
                return


def process_command(command: str, interpreter: Interpreter, file_db: str):
    """
    Interface to fork between 8085 commands and special repl commands
    For 8085 commands, calls preprocessor and interpreter add to list command
    """
    interpreter.state.restore(file_db)
    logger.debug(f"Command received: {command}")
    if command == "help":
        msg_help()
    elif command == "quit":
        exit(0)
    elif command == "inspect":
        interpreter.state.inspect()
    elif command.strip() == "":
        return
    else:
        cmd = cmd_preprocessor(command, interpreter.state)
        if cmd and cmd.is_valid:
            if interpreter.add_command(cmd):
                interpreter.execute_next()
    interpreter.state.save(file_db)


def cmd_preprocessor(cmd: str, state: State) -> Optional[Command]:
    """
    Convert tokens to types, Return a Command object.
    """
    cmd_list = tuple([item.strip() for item in cmd.split(" ") if item])
    logger.debug(f"Splitted commands: {cmd_list}")

    # Preproces comments
    cmd_list = process_comments(cmd_list)
    if not cmd_list:
        logger.debug(f"Statements composed of solely of comments, ending evaluation.")
        return

    # Preproces labels
    label = ""
    if is_label(cmd_list[0]):
        label = cmd_list[0][:-1]
        cmd_list = cmd_list[1:]

    if not cmd_list:
        logger.error(f"Command incomplete: only found label '{label}:'")
        return

    first, second = 0, 1
    cmdname, cmdargs = cmd_list[first], cmd_list[second:]
    if cmdname not in COMMANDS:
        logger.error(f"Command '{cmdname}' not found.")
        return None
    p_cmdargs = process_instruction_args(cmdname, cmdargs)
    if cmdargs and not p_cmdargs:
        return None
    else:
        logger.debug(f"Command {cmdname} found.")
        return Command(cmdname, p_cmdargs, state, label=label)


if __name__ == "__main__":
    args = tuple(sys.argv[1:])
    args, commands, file_db, indirect_mode = process_cmd_line_args(args, logger)
    if args:
        logger.error(
            f"""Invalid argument "{' '.join(args)}": Use "-h" option for help"""
        )
        exit(1)
    logger.debug(f"Got commands {commands} and db file {file_db}")
    main(commands, file_db, indirect_mode)
