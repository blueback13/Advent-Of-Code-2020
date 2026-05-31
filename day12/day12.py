#!/usr/bin/env python3

import argparse
import enum
import functools
import logging


################################################################################


log = logging.getLogger(__name__)


################################################################################


class Headings(enum.Enum):
    """
    Possible headings
    """
    north = 0
    east = 1
    south = 2
    west = 3

    def adjust(self, other) -> enum.Enum:
        """Change heading by 'other' increments"""
        value = self.value
        if not isinstance(other, int):
            raise TypeError("Unsupported operand type", other)

        if other % 90 == 0:
            # Other is divisible by 90
            change = other / 90
        else:
            raise ValueError(
                "Can only adjust headings by increments of 90°!", other,
            )

        value += change
        ret = value % 4
        #log.debug(
        #    "New heading value: %s (raw %s; start %s; change %s)",
        #    ret, value, self.value, change
        #)
        return type(self)(ret)

    def __add__(self, other) -> enum.Enum:
        return self.adjust(other)

    def __sub__(self, other) -> enum.Enum:
        return self.adjust(other)

    @classmethod
    def from_str(cls, name: str):
        """Return the heading described by 'name'"""
        for heading in cls:
            if heading.name.startswith(name.lower()):
                return heading

        raise ValueError("Name does not describe a heading!", name)


################################################################################


class Coordinates():
    """Current Coordinates of a ship"""
    def __init__(self, x: int = 0, y: int = 0) -> None:
        self._x = x
        self._y = y

    @property
    def x(self) -> int:
        """X coordinate of ship"""
        return self._x

    @property
    def y(self) -> int:
        """Y coordinate of ship"""
        return self._y

    @property
    def coordinates(self) -> tuple[int, int]:
        """Y coordinate of ship"""
        return (self.x, self.y)

    def __mul__(self, other):
        """
        Multiply self by other

        - If other is an int, all elements of self will be scaled by it
        - If other is a list with 2 elements, x and y will be scaled by the
          first and second elements respectively
        - All other input is invalid
        """
        match other:
            case _ if isinstance(other, int):
                # Scale self by constant
                return type(self)(self.x * other, self.y * other)
            case [xscale, yscale]:
                return type(self)(self.x * xscale, self.y * yscale)
            case _ if isinstance(other, type(self)):
                return type(self)(self.x * other.x, self.y * other.y)
            case _:
                raise ValueError("Unsupported operand!", other)

    def _add_or_sub(self, other, op = lambda x, o: x + o):
        """
        Scale self by other

        - If other is an int, it will be added to all elements of self
        - If other is a list with 2 elements, the first and second elements will
          be added to x and y respectively
        - All other input is invalid
        """
        match other:
            case _ if isinstance(other, int):
                # Scale self by constant
                return type(self)(op(self.x, other), op(self.y, other))
            case [xdiff, ydiff]:
                return type(self)(op(self.x, xdiff), op(self.y, ydiff))
            case _ if isinstance(other, type(self)):
                return type(self)(op(self.x, other.x), op(self.y, other.y))
            case _:
                raise ValueError("Unsupported operand!", other)

    __add__ = _add_or_sub
    __sub__ = functools.partialmethod(_add_or_sub, op=lambda x, o: x - o)

    def __getitem__(self, item) -> int:
        if not 0 <= item <= 1:
            raise ValueError(
                "Item out of range - only 0 (x) or 1 (y) supported!", item
            )

        return self.coordinates[item]

    def __str__(self) -> str:
        return str(self.coordinates)

    def __repr__(self) -> str:
        return f"Coordinates(x={self.x}, y={self.y})"

################################################################################


class Ship():
    """A ship. Can navigate in all directions and drive forwards"""
    # The base scale
    # e.g. moving 1 unit north adds (1, 0) to the current coordinates
    _base_scales = {
        Headings.north: Coordinates( 0,  1),
        Headings.east : Coordinates( 1,  0),
        Headings.south: Coordinates( 0, -1),
        Headings.west : Coordinates(-1,  0),
    }

    def __init__(
        self, heading: Headings = Headings.east, x: int = 0, y: int = 0,
    ) -> None:
        self._heading = heading
        self._coordinates = Coordinates(x, y)

    @property
    def coordinates(self) -> Coordinates:
        """Current coordinates of ship"""
        return self._coordinates

    @property
    def x(self) -> int:
        """Current X position of ship"""
        return self._coordinates.x

    @property
    def y(self) -> int:
        """Current Y position of ship"""
        return self._coordinates.y

    @property
    def heading(self) -> Headings:
        """Current heading of ship"""
        return self._heading

    def __repr__(self) -> str:
        return f"Ship(heading={self.heading}, x={self.x}, y={self.y})"

    def move(self, direction: Headings, units: int) -> None:
        """Move the ship 'units' units in 'Direction'"""
        log.info(
            "Moving ship %s units %s - current location: %s",
            units, direction.name, self._coordinates,
        )
        self._coordinates += self._base_scales[direction] * units
        log.debug("New location: %s", self._coordinates)

    def forward(self, units: int) -> None:
        """Move 'units' units in the current heading"""
        log.info("Moving %s units forward (%s)", units, self._heading.name)
        self.move(self._heading, units)

    def left(self, degrees: int) -> None:
        """Adjust heading 'degrees' degrees left"""
        self._heading -= degrees

    def right(self, degrees: int) -> None:
        """Adjust heading 'degrees' degrees right"""
        self._heading += degrees

    def manhattan(self):
        """Return the ship's Manhattan distance from the origin (0,0)"""
        return abs(self.x) + abs(self.y)


################################################################################


def part1(commands: list[str]) -> int:
    """Return the Manhattan distance after running commands"""
    ship = Ship()

    for cmd in commands:
        log.info("Running command: %s (ship=%r) ", cmd, ship)
        operation = cmd[0]
        units = int(cmd[1:])

        match operation:
            case "L":
                ship.left(units)
            case "R":
                ship.right(units)
            case "F":
                ship.forward(units)
            case "N" | "E" | "S" | "W":
                direction = Headings.from_str(operation)
                ship.move(direction, units)

        log.debug("After command: ship=%r", ship)

    log.debug("All commands complete! (ship=%r)", ship)
    return ship.manhattan()


################################################################################


def read_commands(in_file: str) -> list[str]:
    """Return a list of commands"""
    with open(in_file) as fh:
        return [l.strip() for l in fh]


################################################################################


if __name__ == "__main__":
    logging.basicConfig()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(
        description="Ship navigator"
    )

    parser.add_argument("input_file")
    parser.add_argument("--part1", action=argparse.BooleanOptionalAction)
    parser.add_argument("--part2", action=argparse.BooleanOptionalAction)

    opts = parser.parse_args()

    commands = read_commands(opts.input_file)

    if opts.part1:
        part1_result = part1(commands)
        print(f"Part 1: {part1_result}")

    if opts.part2:
        log.error("Part 2: Not implemented")
