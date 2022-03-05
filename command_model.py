from collections.abc import Iterable
from typing import Optional

from loguru import logger

from data import COMMANDS, REGISTER_PAIRS
from state_model import State
from converter import hex_to_simple, is_label


class Command:
    def __init__(self, name: str, args: tuple, state: State, label: str = ""):
        self.name = name
        self.args = args
        self.state = state
        self.label = label
        self.is_valid = self.validate()

    def validate(self) -> bool:
        validations = (
            self.validate_args_length(),
            self.validate_args_type(),
        )
        logger.debug(f"Validation Complete {validations}")
        return all(validations)

    def validate_args_length(self) -> bool:
        spec_args = COMMANDS[self.name]["parameters"]
        # Check if parameters dictionary len is equal to given args len
        if len(self.args) != len(spec_args):
            logger.error(
                ValueError(f"Invalid number of arguments for command: {self.name}")
            )
            return False
        return True

    def validate_args_type(self) -> bool:
        spec_params = COMMANDS[self.name]["parameters"]
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
        func = COMMANDS[self.name]["function"]
        class_func = getattr(self, func)
        return class_func(self.args)

    def inspect(self) -> None:
        self.state.inspect()

    def halt(self, args: tuple) -> None:
        logger.debug("HLT received.")
        return

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
        formatted_value = f"0x{int(value, 16):02x}"
        self.state.registers[register] = formatted_value
        logger.debug("MOVED TO IMMEDIATE:" f"{self.state.registers[register]=}")
        print(f"{register} -> {hex_to_simple(formatted_value)}")

    def load_accumulator(self, args: tuple):
        """
        Load accumulator with value from register
        """
        logger.debug(f"LDA: {args}")
        # convert to string representation for dict key
        address = args[0]
        address = f"0x{int(address, 16):04x}"
        if not self.state.memory.get(address):
            logger.debug(
                f"Address {address} is not in memory:",
                f"Creating and init to 0",
            )
            self.state.memory[address] = f"0x{0:02x}"
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
        address = f"0x{int(address, 16):04x}"
        self.state.memory[address] = self.state.accumulator
        logger.debug(
            "STORED ACCUMULATOR:",
            f"{self.state.memory[address]}",
        )
        print(
            f"{hex_to_simple(address)} ->" f" {hex_to_simple(self.state.accumulator)}"
        )

    def store_accumulator_to_register_pair(self, args: tuple) -> None:
        """
        Store accumulator to register pair
        """
        logger.debug(f"STAX: {args}")
        register = args[0]
        REG1, REG2 = REGISTER_PAIRS[register]
        mem_addr = self.state.get_mem_addr_register_pair(register)
        self.state.memory[mem_addr] = self.state.accumulator
        logger.debug(f"Stored from ACCUMULATOR: {self.state.accumulator} to {mem_addr}")
        print(
            f"{REG1}{REG2} [{mem_addr}] -> {hex_to_simple(self.state.accumulator)} [From A]"
        )

    def add(self, args: tuple) -> None:
        """
        Add value from register to accumulator
        """
        logger.debug(f"ADD: {args}")
        register = args[0]
        value = self.state.registers[register]
        acc_value = self.state.accumulator
        self.__add(value)
        logger.debug(f"ADDED: {self.state.accumulator}")
        print(
            f"A -> {hex_to_simple(acc_value)} + {hex_to_simple(value)} -> {hex_to_simple(self.state.accumulator)}\n"
            f"FLAGS: CY->{int(self.state.flags['carry'])}, S->{int(self.state.flags['sign'])}, Z->{int(self.state.flags['zero'])}"
        )

    def add_immediate(self, args: tuple) -> None:
        """
        Add a 8-bit number to Accumulator
        """
        logger.debug(f"Add Immediate: {args}")
        value = args[0]
        acc_value = self.state.accumulator
        self.__add(value)
        logger.debug(f"ADDED: {self.state.accumulator}")
        print(
            f"A -> {hex_to_simple(acc_value)} + {hex_to_simple(value)} -> {hex_to_simple(self.state.accumulator)}\n"
            f"FLAGS: CY->{int(self.state.flags['carry'])}, S->{int(self.state.flags['sign'])}, Z->{int(self.state.flags['zero'])}"
        )

    def subtract_immediate(self, args: tuple) -> None:
        """
        Subtract a 8-bit number from accumulator
        """
        logger.debug(f"Sub Immediate: {args}")
        acc_value = self.state.accumulator  # for logging only
        result = self.__compare_sub_immediate(args)
        self.state.accumulator = result

        value = args[0]
        logger.debug(
            f"Subtracted '{value}' from '{acc_value}': {self.state.accumulator}"
        )
        print(
            f"A -> {hex_to_simple(acc_value)} - {hex_to_simple(value)} -> {hex_to_simple(self.state.accumulator)}\n"
            f"FLAGS: CY->{int(self.state.flags['carry'])}, S->{int(self.state.flags['sign'])}, Z->{int(self.state.flags['zero'])}"
        )

    def subtract(self, args: tuple) -> None:
        """
        Subtract a register from accumulator
        """
        logger.debug(f"Sub Immediate: {args}")
        acc_value = self.state.accumulator
        register = args[0]
        register_value = self.state.registers[register]
        result = self.__compare_sub_immediate((register_value,))
        self.state.accumulator = result

        logger.debug(
            f"Subtracted '{register_value}' from '{acc_value}': {self.state.accumulator}"
        )
        print(
            f"A - {register} -> {hex_to_simple(acc_value)} - {hex_to_simple(register_value)} -> {hex_to_simple(self.state.accumulator)}\n"
            f"FLAGS: CY->{int(self.state.flags['carry'])}, S->{int(self.state.flags['sign'])}, Z->{int(self.state.flags['zero'])}"
        )

    def compare_immediate(self, args: tuple) -> None:
        """
        Compare a 8-bit number from accumulator
        """
        logger.debug(f"Sub Immediate: {args}")
        value = args[0]
        acc_value = self.state.accumulator

        result = self.__compare_sub_immediate(args)
        logger.debug(f"Compared '{value}' from '{acc_value}': {result}")
        print(
            f"[A] {hex_to_simple(acc_value)} - {hex_to_simple(value)} -> {hex_to_simple(result)}\n"
            f"FLAGS: CY->{int(self.state.flags['carry'])}, S->{int(self.state.flags['sign'])}, Z->{int(self.state.flags['zero'])}"
        )

    def compare(self, args: tuple) -> None:
        """
        Subtract a register from accumulator
        """
        logger.debug(f"Sub Immediate: {args}")
        register = args[0]
        register_value = self.state.registers[register]
        acc_value = self.state.accumulator

        result = self.__compare_sub_immediate((register_value,))
        logger.debug(f"Compared '{register_value}' from '{acc_value}': {result}")
        print(
            f"A - {register} -> {hex_to_simple(acc_value)} - {hex_to_simple(register_value)} -> {hex_to_simple(result)}\n"
            f"FLAGS: CY->{int(self.state.flags['carry'])}, S->{int(self.state.flags['sign'])}, Z->{int(self.state.flags['zero'])}"
        )

    def increment_register(self, args: tuple) -> None:
        """
        Increment a given register by 1
        """
        logger.debug(f"INR: {args}")
        register = args[0]
        register_value = self.state.registers[register]
        increment_by = f"0x{1:02x}"
        incremented_int_value = int(register_value, 16) + int(increment_by, 16)
        self.state.registers[register] = hex(abs(incremented_int_value))
        incremented_value = self.state.registers[register]
        logger.debug(f"Incremented: {register} to {incremented_value}")
        print(
            f"{register} -> {hex_to_simple(register_value)} + {hex_to_simple(increment_by)} -> {hex_to_simple(incremented_value)}"
        )

    def decrement_register(self, args: tuple) -> None:
        """
        Decrement a given register by 1
        """
        logger.debug(f"DCR: {args}")
        register = args[0]
        register_value = self.state.registers[register]
        decrement_by = f"0x{1:02x}"  # eq to hex(0x01)
        decremented_int_value = int(register_value, 16) - int(decrement_by, 16)
        if decremented_int_value < 0:
            self.change_state_flags(carry=True, sign=True, zero=False)
        elif decremented_int_value > 0:
            self.change_state_flags(carry=False, sign=False, zero=False)
        elif decremented_int_value == 0:
            self.change_state_flags(carry=False, sign=False, zero=True)
        self.state.registers[register] = hex(abs(decremented_int_value))
        decremented_value = self.state.registers[register]
        logger.debug(f"Decremented: {register} to {decremented_value}")
        print(
            f"{register} -> {hex_to_simple(register_value)} - {hex_to_simple(decrement_by)} -> {hex_to_simple(decremented_value)}"
        )

    def increment_extended_register(self, args: tuple):
        """
        Increment the xtended register pair by 1
        """
        logger.debug(f"INX: {args}")
        register = args[0]
        REG1, REG2 = REGISTER_PAIRS[register]
        register_addr = self.state.get_mem_addr_register_pair(register)
        logger.debug(
            f"Got mem addr stored by register pair {REG1}{REG2}: {register_addr}"
        )
        increment_by = f"0x{1:02x}"
        incremented_int_value = int(register_addr, 16) + int(increment_by, 16)
        incremented_value = f"0x{incremented_int_value:04x}"
        self.state.set_register_pair_value(incremented_value, register)
        hex1, hex2 = self.state.registers[REG1], self.state.registers[REG2]
        logger.debug(f"{REG1} -> {hex1} | {REG2} -> {hex2}")
        print(f"{REG1}{REG2} -> {incremented_value} [{register_addr} + {increment_by}]")

    def decrement_extended_register(self, args: tuple) -> None:
        """
        Decrement the xtended register pair by 1
        """
        logger.debug(f"DCX: {args}")
        register = args[0]
        REG1, REG2 = REGISTER_PAIRS[register]
        register_addr = self.state.get_mem_addr_register_pair(register)
        logger.debug(
            f"Got mem addr stored by register pair {REG1}{REG2}: {register_addr}"
        )
        decrement_by = f"0x{1:02x}"
        decremented_int_value = int(register_addr, 16) - int(decrement_by, 16)
        if decremented_int_value < 0:
            logger.error(
                f"Memory address '{register_addr}' gets negative when decremented"
            )
            return
        decremented_value = f"0x{decremented_int_value:04x}"
        self.state.set_register_pair_value(decremented_value, register)
        hex1, hex2 = self.state.registers[REG1], self.state.registers[REG2]
        logger.debug(f"{REG1} -> {hex1} | {REG2} -> {hex2}")
        print(f"{REG1}{REG2} -> {decremented_value} [{register_addr} - {decrement_by}]")

    def load_register_pair_immediate(self, args: tuple) -> None:
        """
        Load register pair from immediate
        """
        logger.debug(f"LXI: {args}")
        register, value = args[0], args[1]
        value = f"0x{int(value, 16):04x}"
        self.state.set_register_pair_value(value, register)
        REG1, REG2 = REGISTER_PAIRS[register]
        hex1, hex2 = self.state.registers[REG1], self.state.registers[REG2]
        print(f"{REG1}{REG2} -> {value} [{REG1} -> {hex1} {REG2} -> {hex2}]")

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
            f" ; FROM {REG1}{REG2} -> [{hex1}{hex2[2:]}]",
        )

    def jump_if_zero(self, args: tuple) -> Optional[str]:
        """
        Jump to a given label if Zero flag is True
        """
        logger.debug(f"JZ: {args}")
        label = args[0] + ":"
        if not is_label(label):
            logger.debug(f"JZ: Invalid label syntax, '{label[:-1]}'")
        if self.state.flags["zero"]:
            return label[:-1]

    def jump_if_not_zero(self, args: tuple) -> Optional[str]:
        """
        Jump to a given label if Zero flag is False
        """
        logger.debug(f"JNZ: {args}")
        label = args[0] + ":"
        if not is_label(label):
            logger.debug(f"JNZ: Invalid label syntax, '{label[:-1]}'")
        if not self.state.flags["zero"]:
            return label[:-1]

    def jump_if_carry(self, args: tuple) -> Optional[str]:
        """
        Jump to a given label if Carry flag is True
        """
        logger.debug(f"JC: {args}")
        label = args[0] + ":"
        if not is_label(label):
            logger.debug(f"JC: Invalid label syntax, '{label[:-1]}'")
        if self.state.flags["carry"]:
            return label[:-1]

    def jump_if_not_carry(self, args: tuple) -> Optional[str]:
        """
        Jump to a given label if Carry flag is False
        """
        logger.debug(f"JNC: {args}")
        label = args[0] + ":"
        if not is_label(label):
            logger.debug(f"JNC: Invalid label syntax, '{label[:-1]}'")
        if not self.state.flags["carry"]:
            return label[:-1]

    def out(self, args: tuple) -> None:
        """
        Display the vaue of accumulator to display port
        """
        logger.debug(f"OUT: {args}")
        port = args[0]
        acc_value = self.state.accumulator
        print(f"{port}: {hex_to_simple(acc_value)}")

    def change_state_flags(self, **kwargs) -> None:
        """
        Helper function to set state flags in one simple call
        """
        for key, value in kwargs.items():
            if key not in self.state.flags:
                raise ValueError(
                    f"No such flag '{key}' present at state flags {self.state.flags}"
                )
            self.state.flags[key] = value

    def __compare_sub_immediate(self, args: tuple) -> str:
        """
        Variation of compare immediate that changes flags and returns value
        Utilization or reuse for subtraction and comparison
        """
        value = args[0]
        acc_value = self.state.accumulator
        operation_value = int(acc_value, 16) - int(value, 16)
        if operation_value < 0:
            self.change_state_flags(carry=True, sign=True, zero=False)
        elif operation_value > 0:
            self.change_state_flags(carry=False, sign=False, zero=False)
        elif operation_value == 0:
            self.change_state_flags(carry=False, sign=False, zero=True)
        return hex(abs(operation_value))

    def __add(self, value: str) -> None:
        """
        Core logic for both ADD and ADI operations
        """
        acc_value = self.state.accumulator
        operation_value = int(acc_value, 16) + int(value, 16)
        if operation_value > int("0xff", 16):
            self.change_state_flags(carry=True, sign=False, zero=False)
            hex_op_value = f"0x{int(hex(operation_value), 16):02x}"
            carry_discarded_value = f"0x{hex_op_value[-2:]}"
            self.state.accumulator = carry_discarded_value
        elif operation_value == 0:
            self.change_state_flags(carry=False, sign=False, zero=True)
            self.state.accumulator = hex(operation_value)
        else:
            self.change_state_flags(carry=False, sign=False, zero=False)
            self.state.accumulator = hex(operation_value)

    def __str__(self):
        label = f"{self.label}: " if self.label else ""
        return f"{label}{self.name} {' '.join(self.args)}"

    def __repr__(self):
        return f"Command({self.name}, {','.join(self.args)}, label='{self.label}')"
