import os
import sys

from loguru import logger

from data import COMMANDS, LOG_LEVEL_SHORT_FORM, HANDLER_FORMAT
from messages import msg_cli_help


def hex_to_simple(hex_code: str) -> str:
    """
    Convert hex to simple hex 00H representation.
    """
    return hex_code[2:].upper() + "H"


def process_instruction_args(cmdname: str, cmdargs: tuple) -> tuple:
    """
    Processes raw strings arguments of 8085 instruction and tokenize and process them
    """
    processed_cmd_args = list(cmdargs)[:]
    cmd_parameters = COMMANDS[cmdname]["parameters"]
    for (index, argument), p_type in zip(enumerate(cmdargs), cmd_parameters.values()):
        if p_type == "byte":
            logger.debug(f"Processing to hex for '{argument=}'")
            hex_code = process_hex(argument)
            if not hex_code:
                return ()
            processed_cmd_args[index] = hex_code
    return tuple(processed_cmd_args)


def process_hex(argument: str) -> str:
    """
    Convert simple to specify hex string to proper python hexadecimals
    23H -> '0x23'
    2300H -> '0x2300'
    """
    hex_code = argument
    # if the hex argument has H at last, skip the H
    if argument[-1].lower() == "h":
        hex_code = "0x" + argument[:-1]
    else:
        hex_code = "0x" + argument

    # check if given hex code is valid by converting to int
    # if error then its isn't hex and we raise invalid token
    try:
        int(hex_code, 16)
    except ValueError:
        logger.warning(f"hex valid check failed on {hex_code}")
        logger.error(ValueError(f"Invalid token: Expected hex byte got '{argument}'"))
        return ""

    return hex_code


def process_c_mode_args(args: tuple) -> tuple:
    cmd = " ".join(args)
    cmds = [i.strip() for i in cmd.split(";")]
    logger.debug(f"Running in cmd mode: commands {cmds}")
    return tuple(cmds)


def process_file_mode_args(filename: str) -> tuple:
    cmds = []
    if not os.path.exists(filename):
        logger.error(f"No file named {filename} found.")
    with open(filename, "r") as rf:
        # iterating on rf will yeield lines with \n at last
        cmds = [line.strip() for line in rf]
    logger.debug(f"Running in file mode: commands {cmds}")
    return tuple(cmds)


def is_label(token: str) -> bool:
    """
    Determine if a token is a label or not
    Search for : tag basically and make sure it has >=1 letter
    """
    if ":" not in token:
        logger.debug(f"Label check: No labels found when evaluating '{token}'")
        return False

    if token.count(":") > 1:
        logger.debug(f"Label check failed: contains multiple colons {token}")
        return False

    token_parts = [i for i in token.split(":")]
    # when a proper label like (BACK:) is splitted the second item is always '' (prevents ':Back' or 'Bac:k')
    if token_parts[1] != "":
        logger.debug(
            f"Label check failed: contains charecters '{token_parts[1]}' after colon(:) '{token}'"
        )
        return False
    if not token_parts[0].strip():
        logger.debug(f"Label check: Invalid label no charectars only colon '{token}")
        return False

    return True


def process_cmd_line_args(args: tuple, logger) -> tuple:
    log_level = "WARNING"
    indirect_mode = False
    if args and args[0] == "-i":
        indirect_mode = True
        args = args[1:]
    if len(args) > 1 and args[0] == "-v":
        level = args[1]
        log_level = LOG_LEVEL_SHORT_FORM.get(level, log_level)
        args = args[2:]

    logger.remove()
    logger.add(sys.stderr, level=log_level, format=HANDLER_FORMAT)
    logger.add("debug.log", level="DEBUG", rotation="1 MB")

    logger.debug(f"Got cmd args {args}")
    commands, file_db = tuple(), ""
    if args and (args[0] == "help" or args[0] == "--help" or args[0] == "-h"):
        msg_cli_help()
        exit(0)
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
    return (args, commands, file_db, indirect_mode)
