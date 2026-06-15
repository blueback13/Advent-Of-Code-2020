#!/usr/bin/env python3

import argparse
import collections
import enum
import logging
import typing


################################################################################


log = logging.getLogger(__name__)

Point = collections.namedtuple("Point", ["x", "y", "z"])


################################################################################


class State(enum.Enum):
    """Represents the state of a point in the 3D grid"""
    active = "#"
    inactive = "."


################################################################################


class Grid():
    """
    Represent a 3D grid of points, where points can be either active or inactive
    """
    def __init__(self, active: set[Point] = None) -> None:
        if isinstance(active, (set, list, tuple)):
            self._active = set(active)
        elif not active:
            self._active = set()
        else:
            raise TypeError(
                "'active' must be an iterable type or ommitted; was passed an"
                f" {type(active)}", active,
            )

    @classmethod
    def from_file(cls, in_file: str) -> typing.Self:
        """Read an input file and return a Grid"""
        newgrid = cls()
        with open(in_file) as fh:
            y = 0
            for line in fh:
                x = 0
                for value in line.strip():
                    # Note: Input file always has z=0
                    point = Point(x, y, 0)
                    newgrid[point] = State(value)
                    x += 1
                y += 1

        return newgrid

    def __getitem__(self, point: Point) -> State:
        """Return the current state of a point"""
        return State.active if point in self._active else State.inactive

    def __iter__(self) -> set[Point]:
        """Iterate over all active points"""
        for point in self._active:
            yield point

    def __repr__(self) -> str:
        return f"Grid(active={self._active})"

    def is_active(self, point: Point) -> bool:
        """Return True if point is active"""
        return self[point] == State.active

    def set_active(self, point: Point) -> None:
        """Set 'point' to be active"""
        self._active.add(point)

    def set_inactive(self, point: Point) -> None:
        """Set 'point' to be inactive"""
        try:
            self._active.remove(point)
        except KeyError:
            log.debug("Point %s was already inactive", point)

    def __setitem__(self, point: Point, value: State):
        """Set 'point' to be active or inactive"""
        if not isinstance(value, State):
            raise TypeError(
                f"'value' must be a 'State' object (currently {type(value)})",
                point, value,
            )
        if value == State.active:
            self.set_active(point)
        else:
            self.set_inactive(point)


################################################################################


if __name__ == "__main__":
    logging.basicConfig()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(
        description="Ticket field identifier"
    )

    parser.add_argument("input_file")
    parser.add_argument("--part1", action=argparse.BooleanOptionalAction)
    parser.add_argument("--part2", action=argparse.BooleanOptionalAction)

    opts = parser.parse_args()

    #data = read_input(opts.input_file)

    print_input(rules, your_ticket, nearby_tickets)

    if opts.part1:
        result1 = "TODO"
        print(f"Part1: {result1}")

    if opts.part2:
        result2 = "TODO"
        print(f"Part2: {result2}")
