"""
State of Registers and Memory of 8085.
"""
from loguru import logger
from data import REGISTER_PAIRS


class State:
    """
    Represent the State of Registers and Memory
    """

    def __init__(self):
        # Initialize state of registers with 0 hex values
        self.registers = {
            "A": "0x00",
            "B": "0x00",
            "C": "0x00",
            "D": "0x00",
            "E": "0x00",
            "H": "0x00",
            "L": "0x00",
            "M": "0x00",
        }
        # Initialize few memory locations to garbage values
        self.memory = {
            "0x0000": "0x33",
            "0x0001": "0x9A",
            "0x000A": "0x2B",
            "0x000B": "0x34",
        }

    def get_register_pair_value(self, register:str)->str:
        """
        From a register pair storing memory address, grabs the value store in the mem addr

        reg1 = 0x33, reg2 = 0x44 -> mem_addr = 0x3344 -> value at that addr
        """
        # 0x33, 0x44
        REG1, REG2 = REGISTER_PAIRS[register]
        # 0x44 -> 44
        reg2_val = self.registers[REG2][2:]
        # 0x33 + '44' -> 0x3344
        mem_addr = self.registers[REG1] + reg2_val
        # check for addr at memory if no such addr return '0x00' by default
        value_at_mem_addr = self.memory.get(mem_addr, "0x00")
        logger.debug(f"Loaded {value_at_mem_addr} from {mem_addr}")
        return value_at_mem_addr

    def set_register_pair_value(self, value:str, register:str)->None:
        REG1, REG2 = REGISTER_PAIRS[register]
        # Distribute the 16-bit hex in value literally half half to H and L
        # value -> 5533H --> '0x5533' -> [-2:] -> '0x55', '33' -> '0x' + '33'
        assert len(value) == 6
        # value -> '0x5455', first_hex = 0x54 second = '0x' + 55
        first_hex, second_hex = value[:-2], "0x" + value[-2:]
        self.registers[REG1] = first_hex
        self.registers[REG2] = second_hex
        # Special case for M register
        if register == 'H':
            self.registers["M"] = self.get_register_pair_value("H")
        logger.debug(f"Pair {REG1}{REG2} Loaded: {first_hex}, {second_hex}")

    def set_M(self, value:str)->None:
        self.set_register_pair_value(value, register="H")

    def get_M(self)->str:
        return self.get_register_pair_value("H")


    @property
    def accumulator(self) -> str:
        """
        Get the value of the accumulator.
        """
        return self.registers["A"]

    @accumulator.setter
    def accumulator(self, value: str) -> None:
        """
        Set the value of the accumulator.
        """
        self.registers["A"] = value

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
