from loguru import logger
from data import COMMANDS
from state_model import State
from converter import hex_to_simple


class Command:
    def __init__(self, command: str, args: tuple, state: State):
        self.command = command
        self.args = args
        self.state = state
        self.is_valid = self.validate()

    def validate(self) -> bool:
        return self.validate_args_length()

    def validate_args_length(self) -> bool:
        spec_args = COMMANDS[self.command]["parameters"]
        if len(self.args) != len(spec_args):
            logger.error(
                ValueError(f"Invalid number of arguments for command: {self.command}")
            )
            return False
        return True

    def eval(self):
        """
        Get function str from coomand and convert it to self function and call it with args
        """
        logger.debug("Evaluating command: " + str(self))
        func = COMMANDS[self.command]["function"]
        class_func = getattr(self, func)
        return class_func(self.args)

    def inspect(self) -> None:
        self.state.inspect()

    def move_to_immediate(self, args: tuple) -> None:
        """
        Move to immediate position
        """
        logger.debug(f"MVI: {args}")
        register = args[0]
        value = args[1]
        self.state.registers[register] = value
        logger.debug(
            "MOVED TO IMMEDIATE:"
            f"{self.state.registers[register]=}"
        )
        print(f"{register} -> {hex_to_simple(value)}")

    def load_accumulator(self, args: tuple):
        """
        Load accumulator with value from register
        """
        logger.debug(f"LDA: {args}")
        # convert to string representation for dict key
        address = args[0]
        if not self.state.memory.get(address):
            logger.debug(
                f"Address {address} is not in memory:",
                f"Creating and init to 0",
            )
            self.state.memory[address] = hex(0x00)
        self.state.accumulator = self.state.memory[address]
        logger.debug(f"LOADED ACCUMULATOR: {self.state.accumulator}")
        print(
            f"A -> {hex_to_simple(self.state.accumulator)}",
            f"[From {hex_to_simple(address)}]",
        )

    def store_accumulator(self, args):
        """
        Store accumulator to register
        """
        logger.debug(f"STA: {args}")
        address = args[0]
        self.state.memory[address] = self.state.accumulator
        logger.debug(
            "STORED ACCUMULATOR:",
            f"{self.state.memory[address]}",
        )
        print(
            f"{hex_to_simple(address)} ->"
            f" {hex_to_simple(self.state.accumulator)}"
        )

    def add(self, args):
        """
        Add value from register to accumulator
        """
        logger.debug(f"ADD: {args}")
        register = args[0]
        value = self.state.registers[register]
        acc_value = self.state.accumulator
        self.state.accumulator = hex(int(acc_value, 16) + int(value, 16))
        logger.debug(f"ADDED: {self.state.accumulator}")
        print(f"A + {hex_to_simple(value)} -> {hex_to_simple(self.state.accumulator)}")

    def __str__(self):
        return self.command + " " + " ".join(self.args)

    def __repr__(self):
        return f"Command({self.command}, {','.join(self.args)})"
