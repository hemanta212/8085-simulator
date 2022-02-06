from typing import List, Dict

from loguru import logger

from command_model import Command
from state_model import State


class Interpreter:
    def __init__(self):
        """
        Interpreter that adds command to the log, executes the most latest command.

        command_logs : The list containing Command objs.
        command_index_pointer:
        - The pointer that points to index of next command to be executed
        - This pointer typically points to the last item of command_logs
        - However in Jump instruction it may point at any existing index
        - In case, where the jump points to future labels,
        - The is_execution_suspended is set to true and no further command is evaluated. They're only added to list.
        - In such case the wating_label is checked for the future label that's being waited
        - Once the re-evaluater recognizes the label has been defined the pointer resets to pointing last item in list

        labels_map:
        - Whenever a command is added to the command_logs list. The ones with label are indexed in this dict.
        """
        self.state: State = State()
        self.command_logs: List[Command] = []
        self.command_index_pointer: int = -1  # last item of list
        self.is_execution_suspended: bool = False
        self.waiting_label: str = ""
        self.labels_map: Dict[str, int] = {}

    def execute_next(self) -> None:
        """
        Gets the command to run from the command_index_pointer and executes it
        only if the is_execution_suspended is false
        """
        self.revaluate_suspension()

        if self.is_execution_suspended:
            logger.debug(
                f"Suspended mode on: Execution skipped for '{self.command_logs[-1]}'"
            )
            return

        # if the pointer isnot modified; do as normal just execute latest command
        if self.command_index_pointer == -1:
            command_pointed = self.command_logs[self.command_index_pointer]
            logger.debug(f"Pointer at latest command: '{command_pointed}', executing..")
            self.evaluate_command(command_pointed)
        # if the pointer was modified keep executing from that index to latest item.
        else:
            if self.command_index_pointer >= len(self.command_logs):
                logger.debug(
                    f"Pointer increment reached latest: resetting to -1 and executing.."
                )
                self.command_index_pointer = -1
                self.execute_next()
            else:
                command_pointed = self.command_logs[self.command_index_pointer]
                logger.debug(
                    f"Pointer re-oriented to '{command_pointed=}' at '{self.command_index_pointer}'"
                )
                self.command_index_pointer += 1
                self.evaluate_command(command_pointed)
                self.execute_next()

    def revaluate_suspension(self) -> None:
        """
        - When a jump instruction specifies to label not yet created,
        - We suspend all execution and wait for that label to be defined.
        - For each new command added, we check if it has the label that we're waiting for.
        - In such case, we resume the suspension and reset the pointer to point to latest(this) command in the list.
        """
        if not self.is_execution_suspended:
            logger.debug(f"Re-evaluation unnecessary: Execution isn't suspended")
            return

        latest_command = self.command_logs[-1]
        if latest_command.label == self.waiting_label:
            logger.debug(
                f"Re-evaluated: '{latest_command.label}' == '{self.waiting_label}'. Resuming Execution .."
            )
            self.is_execution_suspended = False
            self.command_index_pointer = -1
        else:
            logger.debug(
                f"Re-evaluated: '{latest_command.label}' != '{self.waiting_label}'. Continuing suspension."
            )

    def add_command(self, command: Command) -> bool:
        """
        Does some basic validation and adds a command to end of the list
        Returns: int/None: Index of list where command is added. Check for not None
        """
        command_index = len(self.command_logs)
        if command.label and command.label in self.labels_map:
            logger.error(
                f"Invalid Command Label: '{command.label}' already exists at '{self.labels_map[command.label]}'"
            )
            return False
        elif command.label:
            logger.debug(
                f"Command has label: registering '{command.label}' to labels_map at '{command_index}'."
            )
            self.labels_map[command.label] = command_index

        logger.debug(f"Added '{command}' Command to the list")
        self.command_logs.append(command)
        return True

    def suspend_execution(self, label: str):
        """
        When a jump instruction referneces a label not yet defined. This function is called to suspend execution.
        - It sets self.waiting_label to the label referenced by the jump instruction.
        - It sets self.is_execution_suspended to True
        """
        self.waiting_label = label
        self.is_execution_suspended = True

    def evaluate_command(self, command: Command) -> None:
        """
        Wrapper to command.eval function to interpret its return value.
        It then sets value of command_pointer, waiting_label and is_execution_suspended.
        """
        label = command.eval()
        logger.debug(f"Command '{command}' evaluation complete. Got '{label=}'")
        if not label:
            return

        if label in self.labels_map:
            logger.debug(f"Jumping to '{label=}' at '{self.labels_map[label]}'")
            self.command_index_pointer = self.labels_map[label]
            self.execute_next()
        else:
            logger.debug(
                f"Jumping failed to '{label=}', Suspending Execution until then.."
            )
            self.is_execution_suspended = True
            self.waiting_label = label
