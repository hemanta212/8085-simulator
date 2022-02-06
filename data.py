"""
Dict of supported COMMAND, description, related function and parameters.
"""

# List of 8085 Registers
REGISTERS = (
    "A",
    "B",
    "C",
    "D",
    "E",
    "H",
    "L",
    "M",
)

REGISTER_PAIRS = {
    "H": ["H", "L"],
    "B": ["B", "C"],
    "D": ["D", "E"],
}

COMMANDS = {
    "MOV": {
        "description": "Move data from one register to another",
        "function": "move",
        "parameters": {
            "source": REGISTERS,
            "destination": REGISTERS,
        },
    },
    "MVI": {
        "description": "Move to immediate",
        "function": "move_to_immediate",
        "parameters": {
            "register": REGISTERS,
            "value": "byte",
        },
    },
    "INR": {
        "description": "Increment Register",
        "function": "increment_register",
        "parameters": {
            "register": REGISTERS,
        },
    },
    "DCR": {
        "description": "Decrement Register",
        "function": "decrement_register",
        "parameters": {
            "register": REGISTERS,
        },
    },
    "LXI": {
        "description": "Load register pair immediate",
        "function": "load_register_pair_immediate",
        "parameters": {
            "register_pair": REGISTER_PAIRS,
            "address": "word",
        },
    },
    "LDA": {
        "description": "Load accumulator",
        "function": "load_accumulator",
        "parameters": {
            "address": "word",
        },
    },
    "STA": {
        "description": "Store accumulator",
        "function": "store_accumulator",
        "parameters": {
            "address": "word",
        },
    },
    "HLT": {
        "description": "Halt",
        "function": "halt",
        "parameters": {},
    },
    "ADD": {
        "description": "Add",
        "function": "add",
        "parameters": {
            "register": REGISTERS,
        },
    },
    "ADI": {
        "description": "Add Immediate",
        "function": "add_immediate",
        "parameters": {
            "value": "byte",
        },
    },
    "SUI": {
        "description": "Subtract Immediate",
        "function": "subtract_immediate",
        "parameters": {
            "value": "byte",
        },
    },
    "LDAX": {
        "description": "Load accumulator from register pair",
        "function": "load_accumulator_from_register_pair",
        "parameters": {"register_pair": {k: REGISTER_PAIRS[k] for k in ("B", "D")}},
    },
    "JZ": {
        "description": "Jump If Zero",
        "function": "jump_if_zero",
        "parameters": {"word": "label"},
    },
    "JNZ": {
        "description": "Jump If Not Zero",
        "function": "jump_if_not_zero",
        "parameters": {"word": "label"},
    },
    "JC": {
        "description": "Jump If Carry",
        "function": "jump_if_carry",
        "parameters": {"word": "label"},
    },
    "JNC": {
        "description": "Jump If Not Carry",
        "function": "jump_if_not_carry",
        "parameters": {"word": "label"},
    },
}

HANDLER_FORMAT = (
    "<cyan>{name: >10}</cyan>: |"
    "<level>{level: <8}</level> | "
    "<cyan>{file}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

LOG_LEVEL_SHORT_FORM = {
    "d": "DEBUG",
    "i": "INFO",
    "w": "WARNING",
    "e": "ERROR",
}
