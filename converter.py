import os
from loguru import logger
from state_model import State
from data import REGISTERS


def hex_to_simple(hex_code: str) -> str:
    """
    Convert hex to simple hex 00H representation.
    """
    return hex_code[2:].upper() + "H"


def process_hex(cmdargs: tuple) -> tuple:
    """
    Filter through each arguments and identify and process only the hex ones.
    Convert simple to specify hex string to proper python hexadecimals
    23H -> '0x23'
    2300H -> '0x2300'
    """
    processed_cmd_args = list(cmdargs)[:]
    for index, argument in enumerate(cmdargs):
        # Filter all args specifying a REGISTER
        if argument in REGISTERS:
            continue

        # Now assume every other stuff is hex
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
            logger.error(ValueError(f"Invalid token: {argument}"))
            return ()

        # finally replace the argument in cmd args with processed hex one
        processed_cmd_args[index] = hex_code

    return tuple(processed_cmd_args)


def process_c_mode_args(args: list) -> tuple:
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
