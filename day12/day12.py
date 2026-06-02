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
    east = 90
    south = 180
    west = 270

    def adjust(self, other) -> enum.Enum:
        """Change heading by 'other' increments"""
        if not isinstance(other, int):
            raise TypeError("Unsupported operand type", other)

        if not other % 90 == 0:
            raise ValueError(
                "Can only adjust headings by increments of 90°!", other,
            )

        value = (self.value + other) % 360
        #log.debug("New heading: %s (start %s)", value, self.value)
        return type(self)(value)

    def __add__(self, other) -> enum.Enum:
        return self.adjust(other)

    def __sub__(self, other) -> enum.Enum:
        return self.adjust(-other)

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

    def rotate(self, new_north: Headings):
        """
        Return new coordinates where north is rotated to point to 'new_north'
        """
        old = {
            Headings.north: abs(self.y if self.y > 0 else 0),
            Headings.east : abs(self.x if self.x > 0 else 0),
            Headings.south: abs(self.y if self.y < 0 else 0),
            Headings.west : abs(self.x if self.x < 0 else 0),
        }
        new = {
            new_north      : old[Headings.north],
            new_north + 90 : old[Headings.east ],
            new_north + 180: old[Headings.south],
            new_north + 270: old[Headings.west ],
        }
        return type(self)(
            x=(new[Headings.east ] - new[Headings.west ]),
            y=(new[Headings.north] - new[Headings.south]),
        )

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


class WaypointShip(Ship):
    """
    A waypoint ship

    Can move the waypoint NSEW, rotate the waypoint, and drive to the waypoint
    """
    # Note: Default position of the waypoint is 10 units East, 1 unit North
    def __init__(
            self, x: int = 0, y: int = 0, wpx: int = 10, wpy: int = 1,
    ) -> None:
        super(WaypointShip, self).__init__(x=x, y=y)
        del self._heading
        self._waypoint = Coordinates(x=wpx, y=wpy)

    @property
    def heading(self) -> None:
        return None

    @property
    def wpx(self) -> int:
        """Current X position of Waypoint"""
        return self._waypoint.x

    @property
    def wpy(self) -> int:
        """Current Y position of Waypoint"""
        return self._waypoint.y

    def __repr__(self) -> str:
        return (
            f"WaypointShip(x={self.x}, y={self.y}, wpx={self.wpx},"
            f" wpy={self.wpy})"
        )

    def move(self, direction: Headings, units: int) -> None:
        """Move the waypoint 'units' units in 'Direction'"""
        log.info(
            "Moving waypoint %s units %s - current waypoint: %s",
            units, direction.name, self._waypoint,
        )
        self._waypoint += self._base_scales[direction] * units
        log.debug("New waypoint: %s", self._waypoint)

    def forward(self, units: int) -> None:
        """Drive to waypoint 'units' times"""
        self._coordinates += self._waypoint * units

    def left(self, degrees: int) -> None:
        """Rotate the waypoint left 'degrees' degrees around the origin"""
        log.info(
            "Rotating waypoint %s degrees left (waypoint=%s)",
            degrees, self._waypoint,
        )
        self._waypoint = self._waypoint.rotate(
            new_north=Headings.north - degrees
        )
        log.info("After rotation: waypoint=%s", self._waypoint)

    def right(self, degrees: int) -> None:
        """Rotate the waypoint right 'degrees' degrees around the origin"""
        log.info(
            "Rotating waypoint %s degrees right (waypoint=%s)",
            degrees, self._waypoint,
        )
        self._waypoint = self._waypoint.rotate(
            new_north=Headings.north + degrees
        )
        log.info("After rotation: waypoint=%s", self._waypoint)


################################################################################


class AltShip():
    """An alternative ship. Can navigate in all directions and drive forwards"""
    def __init__(
        self,
        heading: Headings = Headings.east,
        totals: dict[Headings, int] = {},
        forward: int = 0,
    ) -> None:
        self._heading = heading
        self._totals = {
            Headings.north: totals.get(Headings.north, 0),
            Headings.east : totals.get(Headings.east , 0),
            Headings.south: totals.get(Headings.south, 0),
            Headings.west : totals.get(Headings.west , 0),
        }
        self._forward = forward

    @property
    def totals(self) -> dict[Headings, int]:
        """Total distance ship driven in any direction"""

        return self._totals

    @property
    def total_forward(self) -> int:
        """Total units driven forward"""
        return self._forward

    def driven_heading(self, heading: Headings) -> int:
        """Total units driven towards 'heading'"""
        return self._totals[heading]

    @property
    def heading(self) -> Headings:
        """Current heading of ship"""
        return self._heading

    def __repr__(self) -> str:
        return (
            f"AltShip(heading={self.heading}, totals={self.totals},"
            f" forward={self.total_forward})"
        )

    def move(self, direction: Headings, units: int) -> None:
        """Move the ship 'units' units in 'Direction'"""
        log.info(
            "Moving ship %s units %s - current totals: %s",
            units, direction.name, self._totals,
        )
        self._totals[direction] += units
        log.debug("New totals: %s", self._totals)

    def forward(self, units: int) -> None:
        """Move 'units' units in the current heading"""
        log.info("Moving %s units forward (%s)", units, self._heading.name)
        self._forward += units
        self.move(self._heading, units)

    def left(self, degrees: int) -> None:
        """Adjust heading 'degrees' degrees left"""
        self._heading -= degrees

    def right(self, degrees: int) -> None:
        """Adjust heading 'degrees' degrees right"""
        self._heading += degrees

    def manhattan(self):
        """Return the ship's Manhattan distance from the origin (0,0)"""
        return (
            abs(self._totals[Headings.north] - self._totals[Headings.south])
            + abs(self._totals[Headings.east] - self._totals[Headings.west])
        )


################################################################################


def run_commands(commands: list[str], shiptype: object = Ship) -> int:
    """Return the Manhattan distance after running commands"""
    ship = shiptype()

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
        part1_result = run_commands(commands)
        print(f"Part 1: {part1_result}")

    if opts.part2:
        part2_result = run_commands(commands, WaypointShip)
        print(f"Part 2: {part2_result}")
