#!/usr/bin/env python3

import argparse
import copy
import logging


################################################################################


log = logging.getLogger(__name__)


################################################################################


class bitmask():
    """
    Custom bitmask

    36-digit binary value, where each digit can be '0', '1', or 'X'

    When mask is applied to an integer, digits in the integer are overridden
    such that:
    - Every digit in the int that lines up with a '0' or '1' in the mask is
      replaced with the value from the mask
    - Every digit in the int that lines up with an 'X' in the mask is passed
      through unchanged
    """
    def __init__(self, mask: str = None, length: int = 36) -> None:
        """
        Set the mask

        If no mask is provided, create a default mask of all X of 'length'
        """
        if mask:
            self._mask = mask.upper()
        else:
            self._mask = "X" * length

        # Note: Python doesn't really handle bitwise operations as well as I'd
        # like, so we have to do them manually
        #
        # In other languages we could create two masks out of the bitmask:
        # 1. Applied with bitwise OR; contains all 0's except where there's
        #    a 1 in the bitmask
        # 2. Applied with bitwise AND; contains all 1's except where there's a 0
        #    in the bitmask
        self._replacements = {
            i: v
            for i, v in enumerate(self._mask)
            if v != "X"
        }

    def __repr__(self) -> str:
        return f"""bitmask(mask="{self._mask}")"""

    def apply(self, other: int) -> int:
        binary = f"{other:0{len(self._mask)}b}"
        # Note: we can't replace single elements of a string, so use list
        # comprehension to generate a result
        binary = "".join(
            self._replacements.get(i, v)
            for i, v in enumerate(binary)
        )

        return int(binary, base=2)

    def apply_v2(self, other: int) -> list[int]:
        binary = f"{other:0{len(self._mask)}b}"

        ret = [ [] ]

        for i, m in enumerate(self._mask):
            if m == "0":
                append = [ binary[i] ]
            elif m == "1":
                append = [ "1" ]
            else:
                append = [ "0", "1" ]

            match append:
                case [ v ]:
                    for l in ret:
                        l.append(v)
                case [ v1, v2 ]:
                    # Create a copy of every current list
                    new = copy.deepcopy(ret)
                    # First append v1 to every list in the original list
                    for l in ret:
                        l.append(v1)
                    # Then append v2 to every list in the copy
                    for n in new:
                        n.append(v2)
                    # Finally, extend the original list with the new list
                    ret.extend(new)

        return [
            int("".join(b), base=2) for b in ret
        ]


################################################################################


class State():
    """Current state of the program"""
    def __init__(
        self,
        mask: bitmask = None,
        default: int = 0,
        registers: dict[int, int] = None,
    ) -> None:
        self.mask = bitmask() if mask is None else mask
        self._default = default
        self._registers = {} if registers is None else registers

    def __getitem__(self, key: int) -> int:
        """
        Return the registry value at 'key'

        If 'key' hasn't been set yet the default value will be returned
        """
        if not isinstance(key, int):
            raise TypeError("'key' should be an int!", type(key))

        return self._registers.get(key, self._default)

    def __setitem__(self, key: int, value: int) -> int:
        """Set the value at 'key' to value"""
        if not isinstance(key, int) or not isinstance(key, int):
            raise TypeError("'key' and 'value' should be ints!", type(key), type(value))

        actual = self._mask.apply(value)
        log.debug(
            "Setting register '%s' to '%s' (raw %s; mask %s)",
            key, actual, value, self._mask,
        )
        self._registers[key] = actual

    def __iter__(self) -> list[int]:
        """Iterate over the values in the registry"""
        for v in self._registers.values():
            yield v

    def items(self) -> list[tuple[int, int]]:
        """Return all key/value pairs from the registry"""
        for k, v in self._registry.items():
            yield k, v

    def __repr__(self) -> str:
        return (
            f"State(mask={self._mask}, default={self._default},"
            f" registers={self._registers})"
        )

    @property
    def default(self) -> int:
        """The default value for unset registers"""
        return self._default

    @property
    def mask(self) -> bitmask:
        """The current mask for the state"""
        return self._mask

    @mask.setter
    def mask(self, mask: bitmask) -> None:
        if not isinstance(mask, bitmask):
            raise TypeError("Input is not a bitmask instance!", mask)

        self._mask = mask


################################################################################


class State_v2(State):
    """Version 2 of the program state"""
    def __setitem__(self, key: int, value: int) -> int:
        """Set the value at 'key' to value"""
        if not isinstance(key, int) or not isinstance(key, int):
            raise TypeError("'key' and 'value' should be ints!", type(key), type(value))

        keys = self._mask.apply_v2(key)
        log.debug(
            "Setting %s registers to '%s': key=%s; mask=%s: keys=%s",
            len(keys), value, key, self._mask, keys,
        )
        for k in keys:
            self._registers[k] = value


################################################################################

class Command():
    """
    Base command

    Does nothing itself. Is only used to initialise other commands
    """
    # List of available subclasses
    _registry = []

    @staticmethod
    def _match_command(cmd: str) -> bool:
        """Return True if this subclass works on cmd"""
        raise RuntimeError("_match_command() not overridden!", cmd)

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Initialise a new command type
        """
        super().__init_subclass__(**kwargs)
        cls._registry.append(cls)

    def __new__(cls, cmd: str, *args, **kwargs):
        """Return an object of the appropriate subclass for input SeatState"""
        for newcls in cls._registry:
            if newcls._match_command(cmd):
                obj = super().__new__(newcls)
                obj.__init__(cmd, *args, **kwargs)
                return obj

        if not newcls:
            raise RuntimeError("No handler for command!", state)

    def __init__(self, cmd: str, value) -> None:
        """Set value for command to 'value'"""
        self._cmd = cmd
        self._value = value

    def run(self, state: State) -> None:
        """Run command on state"""
        raise RuntimeError(
            "Command not defined for current class!", self.__class__,
        )

    @property
    def value(self):
        return self._value

    @property
    def cmd(self) -> str:
        return self._cmd

    def __repr__(self) -> str:
        return f"Command(cmd={self.cmd!r}, value={self._value!r})"

    def __str__(self) -> str:
        # Note - we deliberately use the properties here so subclasses can
        # override them
        return f"{self.cmd} = {self.value}"


################################################################################


class MaskCommand(Command):
    """Update the mask of 'state' to 'value'"""
    @staticmethod
    def _match_command(cmd: str) -> bool:
        """Return True for 'mask' commands"""
        return cmd.startswith("mask")

    def __init__(self, cmd: str, value: bitmask) -> None:
        super().__init__(cmd, bitmask(value))

    def run(self, state: State) -> None:
        state.mask = self._value


################################################################################


class MemCommand(Command):
    """Update a register of 'state' to 'value'"""
    @staticmethod
    def _match_command(cmd: str) -> bool:
        """Return True for 'mem' commands"""
        return cmd.startswith("mem")

    def __init__(self, cmd: str, value: bitmask) -> None:
        realcmd, address = cmd.split('[')
        super().__init__(realcmd, int(value))
        self._address = int(address.strip("[]"))

    def run(self, state: State) -> None:
        state[self.address] = self.value

    @property
    def cmd(self) -> str:
        return f"{super().cmd}[{self.address}]"

    @property
    def address(self) -> int:
        return self._address


################################################################################


def run_commands(commands: list[Command], state_type: object = State) -> int:
    """Return total after completing commands"""
    state = state_type()

    for cmd in commands:
        cmd.run(state)

    return sum([v for v in state])


################################################################################


def read_input(in_file: str) -> list[Command]:
    """Read input from file"""
    ret = []
    with open(in_file) as fh:
        for line in fh:
            cmd, value = line.split("=")
            ret.append(Command(cmd.strip(), value.strip()))

    return ret


################################################################################


if __name__ == "__main__":
    logging.basicConfig()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(
        description="Bus timetable reader"
    )

    parser.add_argument("input_file")
    parser.add_argument("--part1", action=argparse.BooleanOptionalAction)
    parser.add_argument("--part2", action=argparse.BooleanOptionalAction)

    opts = parser.parse_args()

    commands = read_input(opts.input_file)

    if opts.part1:
        result1 = run_commands(commands)
        print(f"Part1: {result1}")

    if opts.part2:
        result2 = run_commands(commands, state_type=State_v2)
        print(f"Part2: {result2}")

