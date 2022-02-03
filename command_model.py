from collections.abc import Iterable
from loguru import logger
from data import COMMANDS, REGISTER_PAIRS
from state_model import State
from converter import hex_to_simple


class Command:
    def __init__(self, command: str, args: tuple, state: State):
        self.command = command
        self.args = args
        self.state = state
        self.is_valid = self.validate()

    def validate(self) -> bool:
        validations = (
            self.validate_args_length(),
            self.validate_args_type(),
        )
        logger.debug(f"Validation Complete {validations}")
        return all(validations)

    def validate_args_length(self) -> bool:
        spec_args = COMMANDS[self.command]["parameters"]
        # Check if parameters dictionary len is equal to given args len
        if len(self.args) != len(spec_args):
            logger.error(
                ValueError(f"Invalid number of arguments for command: {self.command}")
            )
            return False
        return True

    def validate_args_type(self) -> bool:
        spec_params = COMMANDS[self.command]["parameters"]
        # Now if type of parameter is an iterable, validate if give arg in inside it
        for given_arg, (p_name, p_type) in zip(self.args, spec_params.items()):
            if isinstance(p_type, Iterable) and not isinstance(p_type, str):
                if given_arg not in p_type:
                    logger.error(
                        TypeError(f"Got '{given_arg}' for parameter of type {p_name}")
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

    def move(self, args: tuple) -> None:
        """
        Move value from register to register
        """
        logger.debug(f"MOV: {args}")
        register_to, register_from = args[0], args[1]
        value = self.state.registers[register_from]
        self.state.registers[register_to] = value
        logger.debug(f"MOVED: {register_to}[{value}] <- {register_from}")
        print(f"{register_to} -> {hex_to_simple(value)} [From {register_from}]")

    def move_to_immediate(self, args: tuple) -> None:
        """
        Move to immediate position
        """
        logger.debug(f"MVI: {args}")
        register = args[0]
        value = args[1]
        self.state.registers[register] = value
        logger.debug("MOVED TO IMMEDIATE:" f"{self.state.registers[register]=}")
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

    def store_accumulator(self, args: tuple) -> None:
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
            f"{hex_to_simple(address)} ->" f" {hex_to_simple(self.state.accumulator)}"
        )

    def add(self, args: tuple) -> None:
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

    def load_register_pair_immediate(self, args: tuple) -> None:
        """
        Load register pair from immediate
        """
        logger.debug(f"LXI: {args}")
        register, value = args[0], args[1]
        self.state.set_register_pair_value(value, register)
        REG1, REG2 = REGISTER_PAIRS[register]
        hex1, hex2 = self.state.registers[REG1], self.state.registers[REG2]
        print(f"{REG1} -> {hex1}\n{REG2} -> {hex2}")

    def load_accumulator_from_register_pair(self, args: tuple) -> None:
        """
        Load accumulator from register pair
        """
        logger.debug(f"LDAX: {args}")
        register = args[0]
        REG1, REG2 = REGISTER_PAIRS[register]
        hex1, hex2 = self.state.registers[REG1], self.state.registers[REG2]
        value = self.state.get_register_pair_value(register)
        self.state.accumulator = value
        logger.debug(f"LOADED ACCUMULATOR: {self.state.accumulator}")
        print(
            f"A -> {hex_to_simple(self.state.accumulator)}",
            f"\nFROM {REG1}{REG2} -> [{hex1}{hex2[2:]}]"
        )

    def __str__(self):
        return self.command + " " + " ".join(self.args)

    def __repr__(self):
        return f"Command({self.command}, {','.join(self.args)})"
