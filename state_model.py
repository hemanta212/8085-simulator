"""
State of Registers and Memory of 8085.
"""
import os
import json
from typing import Dict

from loguru import logger

from data import REGISTER_PAIRS
from custom_dictionaries import RegisterDict, MemoryDict


class State:
    """
    Represent the State of Registers and Memory
    """

    def __init__(self):
        # Initialize few memory locations to garbage values
        self.memory: MemoryDict = MemoryDict()
        self.memory.update(
            {
                "0x1000": "0x2B",
                "0x1001": "0x34",
            }
        )
        # Initialize state of registers with 0 hex values
        self.registers: RegisterDict = RegisterDict(self)
        self.registers.update(
            {
                "A": "0x00",
                "B": "0x00",
                "C": "0x00",
                "D": "0x00",
                "E": "0x00",
                "H": "0x00",
                "L": "0x00",
                "M": "0x00",
            }
        )
        # Initialize the flags
        self.flags: Dict[str, bool] = {
            "carry": False,
            "auxillary_carry": False,
            "zero": False,
            "sign": False,
        }

    def get_mem_addr_register_pair(self, register: str) -> str:
        """
        Gets the 16-bit memory adress combinely stored by an extended register pairs

        reg1 = 0x33, reg2 = 0x44 -> mem_addr = 0x3344
        """
        # let REG1->0x33, REG2->0x44
        REG1, REG2 = REGISTER_PAIRS[register]
        # 0x44 -> 44
        reg2_val = self.registers[REG2][2:]
        # 0x33 + '44' -> 0x3344
        mem_addr = self.registers[REG1] + reg2_val
        return mem_addr

    def get_register_pair_value(self, register: str) -> str:
        """
        From a register pair storing memory address, grabs the value store in the mem addr

        reg1 = 0x33, reg2 = 0x44 -> mem_addr = 0x3344 -> value at that addr
        """
        mem_addr = self.get_mem_addr_register_pair(register)
        # check for addr at memory if no such addr return '0x00' by default
        value_at_mem_addr = self.memory.get(mem_addr, "0x00")
        logger.debug(f"Loaded {value_at_mem_addr} from {mem_addr}")
        return value_at_mem_addr

    def set_register_pair_value(self, value: str, register: str) -> None:
        """
        Takes a 16 bit value and splits it between register pairs
        """
        REG1, REG2 = REGISTER_PAIRS[register]
        # Distribute the 16-bit hex in value literally half half to H and L
        # value -> 5533H --> '0x5533' -> [-2:] -> '0x55', '33' -> '0x' + '33'
        assert len(value) == 6
        # value -> '0x5455', first_hex = 0x54 second = '0x' + 55
        first_hex, second_hex = value[:-2], "0x" + value[-2:]
        self.registers[REG1] = first_hex
        self.registers[REG2] = second_hex
        # Special case for M register
        if register == "H":
            self.registers["M"] = self.get_register_pair_value("H")
        logger.debug(f"Pair {REG1}{REG2} Loaded: {first_hex}, {second_hex}")

    @property
    def accumulator(self) -> str:
        """
        Get the value of the accumulator.
        """
        value = self.registers["A"]
        formatted_value = f"0x{int(value, 16):02x}"
        return formatted_value

    @accumulator.setter
    def accumulator(self, value: str) -> None:
        """
        Set the value of the accumulator.
        """
        formatted_value = f"0x{int(value, 16):02x}"
        self.registers["A"] = formatted_value

    def inspect(self) -> None:
        """
        Inspect the State of Registers and Memory
        """
        logger.info("Registers:")
        print("Registers:")
        for key, value in self.registers.items():
            print("\t{}: {}".format(key, value))
        logger.info("Memory:")
        print("\nMemory:")
        for key, value in self.memory.items():
            print("\t{}: {}".format(key, value))
        logger.info("Flags:")
        print("\nFlags:")
        for key, value in self.flags.items():
            print("\t{}: {}".format(key, int(value)))

    def restore(self, file_db: str) -> None:
        if not file_db or not os.path.exists(file_db):
            return

        with open(file_db, "r") as rf:
            file_data = rf.read()
            if not file_data.strip():
                return

        with open(file_db, "r") as rf:
            state_data = json.load(rf)

        self.memory = MemoryDict()
        self.memory.update(state_data["memory"])
        self.registers = RegisterDict(self)
        self.registers.update(state_data["registers"])

    def save(self, file_db: str) -> None:
        if not file_db:
            return
        if not os.path.exists(file_db):
            with open(file_db, "w"):
                pass

        reg_data = {k: v for k, v in self.registers.items()}
        mem_data = {k: v for k, v in self.memory.items()}
        state_data = {"registers": reg_data, "memory": mem_data}
        with open(file_db, "w") as wf:
            json.dump(state_data, wf)
