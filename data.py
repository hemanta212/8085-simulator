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

COMMANDS = {
    'MVI': {
        'description': 'Move to immediate',
        'function': 'move_to_immediate',
        'parameters': {
            'register': REGISTERS,
            'value': 'byte',
        }
    },
    'LXI': {
        'description': 'Load register pair immediate',
        'function': 'load_register_pair_immediate',
        'parameters': {
            'register_pair': REGISTERS,
            'value': 'word',
        }
    },
    'LDA': {
        'description': 'Load accumulator',
        'function': 'load_accumulator',
        'parameters': {
            'address': 'word',
        }
    },
    'STA': {
        'description': 'Store accumulator',
        'function': 'store_accumulator',
        'parameters': {
            'address': 'word',
        }
    },
    'HLT': {
        'description': 'Halt',
        'function': 'halt',
        'parameters': {},
    },
    'ADD': {
        'description': 'Add',
        'function': 'add',
        'parameters': {
            'register': REGISTERS,
        }
    },
}

