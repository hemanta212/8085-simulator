"""
State of Registers and Memory of 8085.
"""
from loguru import logger


class State:
    """
    Represent the State of Registers and Memory
    """

    def __init__(self):
        # Initialize state of registers with 0 hex values
        self.registers = {
            "A": '0x00',
            "B": '0x00',
            "C": '0x00',
            "D": '0x00',
            "E": '0x00',
            "H": '0x00',
            "L": '0x00',
        }
        # Initialize few memory locations to garbage values
        self.memory = {
            "0x0000": "0x33",
            "0x0001": "0x9A",
            "0x000A": "0x2B",
            "0x000B": "0x34",
        }

    @property
    def accumulator(self) -> str:
        """
        Get the value of the accumulator.
        """
        return self.registers["A"]

    @accumulator.setter
    def accumulator(self, value:str) -> None:
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
