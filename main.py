"""
An 8085 interpreter written in Python.
"""
import sys
from loguru import logger
from rich import print

from command_model import Command
from state_model import State
from data import COMMANDS, HANDLER_FORMAT, LOG_LEVEL_SHORT_FORM
from messages import msg_welcome, msg_help, msg_cli_help
from converter import process_hex, process_c_mode_args, process_file_mode_args


def main(commands: tuple = tuple(), file_db: str = "", indirect_mode: bool = False):
    state = State()
    for command in commands:
        process_command(command, state, file_db)

    if not commands:
        if not indirect_mode:
            msg_welcome()
        while True:
            try:
                command = input(">>>") if not indirect_mode else input("")
                process_command(command, state, file_db)
            except EOFError:
                return


def process_command(command: str, state: State, file_db: str):
    """
    Interface to fork between 8085 commands and special repl commands
    For 8085 commands, calls preprocessor and evalulator
    """
    state.restore(file_db)
    logger.debug(f"Command received: {command}")
    if command == "help":
        msg_help()
    elif command == "quit":
        exit(0)
    elif command == "inspect":
        state.inspect()
    else:
        cmd = cmd_preprocessor(command, state)
        if cmd is not None and cmd.is_valid:
            cmd.eval()
    state.save(file_db)


def cmd_preprocessor(cmd: str, state: State) -> Command:
    """
    Convert tokens to types, Return a Command object.
    """
    cmd_list = tuple([item.strip() for item in cmd.split(" ") if item])
    logger.debug(f"Splitted commands: {cmd_list}")
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
    args = sys.argv[1:]
    log_level = "WARNING"
    # When running from other process donot display the welcome or >>> prompt
    indirect_mode = False
    if args and args[0] == "-i":
        indirect_mode = True
        args = args[1:]
    if len(args) > 1 and args[0] == "-v":
        level = args[1]
        log_level = LOG_LEVEL_SHORT_FORM.get(level, "WARNING")
        args = args[2:]
    else:
        logger.remove()
        logger.add(sys.stderr, level=log_level, format=HANDLER_FORMAT)
        logger.add("debug.log", level="DEBUG", rotation="1 MB")

    logger.debug(f"Got cmd args {args}")
    commands, file_db = tuple(), ""
    if args and (args[0] == "help" or args[0] == "--help" or args[0] == "-h"):
        msg_cli_help()
        exit(1)
    if len(args) > 1 and args[0] == "-db":
        filename = args[1]
        file_db = filename
        args = args[2:]
    if len(args) > 1 and args[0] == "-f":
        commands = process_file_mode_args(args[1])
        args = args[2:]
    if len(args) > 1 and args[0] == "-c":
        commands = process_c_mode_args(args[1:])
        args = args[2:]

    if args:
        logger.error(
            f"""Invalid argument "{' '.join(args)}": Use "-h" option for help"""
        )
        exit(1)

    logger.debug(f"Got commands {commands} and db file {file_db}")
    main(commands, file_db, indirect_mode)
