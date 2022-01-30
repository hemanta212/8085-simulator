"""
Represent the State of Registers and Memory of 8085.
"""
from loguru import logger

class State:
    """
    Represent the State of Registers and Memory of 8085.
    """
    def __init__(self):
        """
        Initialize the State of Registers and Memory of 8085.
        """
        # Initialize state of registers with garbage hex values
        self.registers = {"A": 0x00, "B": 0x00, "C": 0x00, "D": 0x00, "E": 0x00, "H": 0x00, "L": 0x00}
        self.memory = {}

    @property
    def accumulator(self):
        """
        Get the value of the accumulator.
        """
        return self.registers['A']

    @accumulator.setter
    def accumulator(self, value):
        """
        Set the value of the accumulator.
        """
        self.registers['A'] = value

    def inspect(self):
        """
        Inspect the State of Registers and Memory of 8085.
        """
        logger.info("Registers:")
        print("Registers:")
        for key, value in self.registers.items():
            print("\t{}: {}".format(key, value))
        logger.info("Memory:")
        print("\nMemory:")
        for key, value in self.memory.items():
            print("\t{}: {}".format(key, value))

