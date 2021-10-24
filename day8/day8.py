#!/usr/bin/env python3
"""
Script to solve day 8 of the 2020 Advent of Code.

https://adventofcode.com/2020/day/8
"""

import functools
import logging
import re
from typing import Tuple, Dict, Union

################################################################################

log = logging.getLogger(__name__)

COMMAND_RE = r"^(?P<cmd>[a-zA-Z]{3}) (?P<num>[-+]\d*)$"

################################################################################

class Context:
    """Class representing a programs current state."""

    def __init__(self):
        # Set the accumulator and 'instruction pointer'.
        self._accumulator = 0
        self._instruction = 0

    ########################################

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}(accumulator={self.value}, "
            f"instruction={self.instruction})>"
        )

    ########################################

    def accumulate(self, num: int):
        """Accumulate"""
        log.info(
            f"{'Increasing' if num >=0 else 'Decreasing'} accumulator by {num}."
        )
        self._accumulator += num

    ########################################

    def jump(self, num: int):
        log.info(
            f"Jumping {'forward' if num >=0 else 'backward'} {num} commands."
        )
        if num < 0 and abs(num) > self._instruction:
            raise RuntimeError(
                f"Cannot jump back more than {self._instruction} commands!"
            )
        self._instruction += num

    ########################################

    next_cmd = functools.partialmethod(jump, 1)

    ########################################

    @property
    def value(self):
        return self._accumulator

    ########################################

    @property
    def instruction(self):
        return self._instruction

################################################################################

class Command:
    """Class to represent commands."""

    __commands = set()

    ########################################

    def __init__(self, name: str, num: int):
        self.name = name
        self.num = num

    ########################################

    def __repr__(self):
        return f"<{self.__class__.__name__}(name={self.name!r}, num={self.num})>"

    ########################################

    def handle_cmd(self, ctx: Context):
        log.warning(f"Command {self.name} handled by base class (noop).")
        ctx.next_cmd()

    ########################################

    @classmethod
    def handles(cls, name: str):
        """Return true if this class handles a command with 'name'."""
        return False

    ########################################

    @classmethod
    def register_command(cls, command):
        """Register a class prototype."""
        if issubclass(command, cls) and command is not cls:
            cls.__commands.add(command)
        else:
            log.error("Cannot register command")

    ########################################

    def __new__(cls, name: str, *args, **kwargs):
        """Instantiate a command instance"""
        for command in cls.__commands:
            if command.handles(name):
                return object.__new__(command)

        raise RuntimeError(f"No class to handle command {name}", name)

################################################################################

class nopCommand(Command):
    """Handles the 'nop' command"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    ########################################

    def handle_cmd(self, ctx: Context):
        log.info(f"Command {self.name} is a null operation.")
        ctx.next_cmd()

    ########################################

    @classmethod
    def handles(cls, name: str):
        """Return true if this class handles a command with 'name'."""
        if name == "nop":
            return True

        return False

################################################################################

class jmpCommand(Command):
    """Handles the 'jmp' command"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    ########################################

    def handle_cmd(self, ctx: Context):
        log.info(f"Command {self.name} is a jump operation.")
        ctx.jump(self.num)

    ########################################

    @classmethod
    def handles(cls, name: str):
        """Return true if this class handles a command with 'name'."""
        if name == "jmp":
            return True

        return False

################################################################################

class accCommand(Command):
    """Handles the 'acc' command"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    ########################################

    def handle_cmd(self, ctx: Context):
        log.info(f"Command {self.name} is an acc operation.")
        ctx.accumulate(self.num)
        ctx.next_cmd()

    ########################################

    @classmethod
    def handles(cls, name: str):
        """Return true if this class handles a command with 'name'."""
        if name == "acc":
            return True

        return False

################################################################################

# Register the command prototypes.
Command.register_command(nopCommand)
Command.register_command(jmpCommand)
Command.register_command(accCommand)

################################################################################

def parse_program(filename: str) -> Tuple[str, int]:
    """Parses a program from a file."""
    regex = re.compile(COMMAND_RE)
    with open(filename, "r") as fh:
        for line in fh.readlines():
            line = line.strip()
            log.debug(f"Got a program line '{line}'")
            match = regex.match(line)
            if not bool(match):
                raise RuntimeError("Line '{line}' is formatted incorrectly.")
            yield match.group("cmd"), int(match.group("num"))

################################################################################

class Program:
    """Represent a program as a list of commands."""

    def __init__(self, filename: str):
        self._file = filename
        self._program = []  # To store already processed commands.
        self._parser = parse_program(self._file)
        self._len = None

    ########################################

    def __repr__(self):
        return (
            f"<{self.__class__.__name__}(file={self._file!r},"
            f" length={len(self)})>"
        )

    ########################################

    def _gen_commands(self, target: int):
        """Generate commands until at least 'target' have been retrieved."""
        log.info(
            f"Ensuring {target} commands are processed (currently "
            f"{len(self._program)} have been processed)"
        )
        for _ in range(max(0, target - len(self._program))):
            name, num = next(self._parser)
            log.debug(f"Generating command for {name}")
            self._program.append(Command(name, num))

    ########################################

    def __getitem__(self, item):
        """Get elements of the program."""
        if type(item) is int:
            self._gen_commands(item + 1)
        elif type(item) is slice:
            self._gen_commands(max(abs(item.start), abs(item.stop)))
        else:
            raise TypeError("Item is invalid", item)

        return self._program[item]

    ########################################

    def __len__(self):
        if self._len is None:
            self._len = sum(
                1 for line in open(self._file) if line.strip() != ""
            )
        return self._len

################################################################################

class OverrideProgram(Program):
    """A program class that allows instructions to be overriden."""

    def __init__(self, file_or_program: Union[str, Program]):
        """file_or_program: either a filename or an existing program object"""
        self._overrides = {}

        if isinstance(file_or_program, Program):
            self._real_program = file_or_program
        else:
            self._real_program = Program(file_or_program)

        self._file = self._real_program._file

    ########################################

    def __len__(self):
        return len(self._real_program)

    ########################################

    def __getitem__(self, item):
        """Get elements of the program."""
        override = self._overrides.get(item)
        if override is not None:
            log.info(f"Comand at {item} overriden!")
            return override

        return self._real_program[item]

    ########################################

    def override(self, instruction: int, command: Command):
        """
        Override a command.

        Parameters:
        instruction: Positional instruction to override.
        command    : Command to use instead.
        """
        self._overrides[instruction] = command

    ########################################

    def clear_override(self, instruction: int):
        """Clear an overriden command"""
        del self._overrides[instruction]

    ########################################

    def clear_overrides(self):
        """Clear all overriden commands"""
        self._overrides.clear()

    ########################################

    @property
    def total_overrides(self):
        return len(self._overrides)

################################################################################

def operate(program: Program) -> int:
    """
    Run a program.

    Keeps track of operations that have been performed; errors if an operation
    is performed twice

    Returns the value of the accumulator.
    """
    ctx = Context()
    visited = []

    log.info("Running program...")

    while ctx.instruction not in visited and len(program) > ctx.instruction:
        visited.append(ctx.instruction)
        cmd = program[ctx.instruction]
        cmd.handle_cmd(ctx)

    if ctx.instruction in visited:
        raise RuntimeError(
            f"Cycle detected! (Accumulator value {ctx.value})", ctx, visited
        )

    return ctx.value

################################################################################

def cycle_detector(program: Program) -> int:
    """
    Run a program to detect cycles within it.

    Uses Floyd's tortoise and hare algorithm.

    Note: detects the cycle, but at the command that is corrupted.
    """
    tortoise = Context()
    hare = Context()

    condition = False

    while not condition:
        # Advance the tortoise once
        log.info(f"Advancing tortoise (instruction {tortoise.instruction})")
        program[tortoise.instruction].handle_cmd(tortoise)

        # Advance the hare twice
        log.info(f"Advancing hare (instruction {hare.instruction})")
        program[hare.instruction].handle_cmd(hare)
        if not hare.instruction >= len(program):
            log.info(f"Advancing hare again (instruction {hare.instruction})")
            program[hare.instruction].handle_cmd(hare)
        else:
            log.warning(
                f"Hare terminated (instruction {hare.instruction} out of"
                f" {len(program)}"
            )
            return hare.instruction

        condition = tortoise.instruction == hare.instruction

        if not condition and hare.instruction >= len(program):
            log.warning(
                f"Hare terminated (instruction {hare.instruction} out of"
                f" {len(program)}"
            )
            return hare.instruction

    log.info(
        f"Hare and Tortoise caught each other at instruction {hare.instruction}"
    )
    return hare.instruction

################################################################################

def operate_repair(program: Program) -> int:
    """Operate on a program; attempting to repair any cycles."""

    result = None
    oprogram = OverrideProgram(program)

    visited = None
    backcommand = -1  # Reverse indice of the next failed command to try

    while result is None:
        log.info("Running program")
        try:
            return operate(oprogram)
        except RuntimeError as err:
            if visited is None:
                visited = err.args[2]

            oprogram.clear_overrides()

            while oprogram.total_overrides == 0:
                command = oprogram[visited[backcommand]]

                if isinstance(command, jmpCommand):
                    log.info(
                        f"Replacing command {visited[backcommand]} with a nop"
                        " command."
                    )
                    oprogram.override(
                        visited[backcommand], Command('nop', command.num)
                    )
                elif isinstance(command, nopCommand):
                    log.info(
                        f"Replacing command {visited[backcommand]} with a jmp"
                        " command."
                    )
                    oprogram.override(
                        visited[backcommand], Command('jmp', command.num)
                    )

                # Reduce the index so we get teh correct command next time.
                backcommand -= 1
