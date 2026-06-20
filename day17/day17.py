#!/usr/bin/env python3

import argparse
import collections
import enum
import logging
import typing


################################################################################


log = logging.getLogger(__name__)

Point = collections.namedtuple("Point", ["x", "y", "z"])

# Calculate relative positions of points that surround a point on a 3D grid
relative_surrounding = {
    (x, y, z)
    for x in range(-1,2)
    for y in range(-1,2)
    for z in range(-1,2)
    if not x == y == z == 0
}


################################################################################


class State(enum.Enum):
    """Represents the state of a point in the 3D grid"""
    active = "#"
    inactive = "."


################################################################################


def get_surrounding_points(point: Point) -> set[Point]:
    """Return all points that surround a given point"""
    for x, y, z in relative_surrounding:
        yield Point(
            x = point.x + x,
            y = point.y + y,
            z = point.z + z,
        )


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
                    value = State(value)
                    log.debug("Setting point %s to %s", point, value)
                    newgrid[point] = value
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

    def __len__(self) -> int:
        """Return number of active points"""
        return len(self._active)

    def __repr__(self) -> str:
        return f"Grid(active={self._active})"

    def __str__(self) -> str:
        # Calculate the min and max x, y, and z values we need to consider
        minx = maxx = miny = maxy = minz = maxz = 0
        for point in self:
            minx = point.x if point.x < minx else minx
            maxx = point.x if point.x > maxx else maxx
            miny = point.y if point.y < miny else miny
            maxy = point.y if point.y > maxy else maxy
            minz = point.z if point.z < minz else minz
            maxz = point.z if point.z > maxz else maxz

        # Now that we have the ranges we can generate the grid
        layers = []
        for z in range(minz, maxz+1):
            rows = []
            for y in range(miny, maxy+1):
                rows.append(
                    "".join([
                        self[Point(x, y, z)].value for x in range(minx, maxx+1)
                    ])
                )
            layers.append("\n".join(rows))

        return "\n\n".join([
            f"z={z}\n{layer}"
            for z, layer in zip(range(minz, maxz+1), layers)
        ])

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

    def part1_run_cycle(self) -> None:
        """
        Update self as per the rules from part 1

        Rules:
        - If a cube (point) is active and exactly 2 or 3 of its neighbors are
          also active, the cube remains active. Otherwise, the cube becomes
          inactive.
        - If a cube (point) is inactive but exactly 3 of its neighbors are
          active, the cube becomes active. Otherwise, the cube remains inactive.
        """
        # Dict; each point that has a key in the dict has at least one active
        # point as a neighbour
        # Type hint: dict[Point, set[Point]]
        active_adjacent = {}

        for active in self:
            for neighbour in get_surrounding_points(active):
                current_neighbouring = active_adjacent.get(neighbour, set())
                current_neighbouring.add(active)
                active_adjacent[neighbour] = current_neighbouring

            # Make sure the current point is also in the dict if it hasn't
            # already been added.
            # This insures an active point with no active neighbours will
            # actually be set inactive
            active_adjacent[active] = active_adjacent.get(active, set())

        for point, active_neighbours in active_adjacent.items():
            # Note: any given point will not have its state changed until we
            # check it here, so we can rely on the is_active() method here.
            if self.is_active(point) and not (2 <= len(active_neighbours) <= 3):
                log.debug(
                    "Point %s active, setting inactive: (count %s;"
                    " adjacent: %s)",
                    point, len(active_neighbours), active_neighbours,
                )
                self.set_inactive(point)
            elif not self.is_active(point) and len(active_neighbours) == 3:
                log.debug(
                    "Point %s inactive, setting active: (count: %s;"
                    " adjacent: %s)",
                    point, len(active_neighbours), active_neighbours
                )
                self.set_active(point)
            else:
                log.debug(
                    "Point %s is %s, not changing: (count: %s; adjacent: %s)",
                    point,
                    "active" if self.is_active(point) else "inactive",
                    len(active_neighbours),
                    active_neighbours
                )


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

    grid = Grid.from_file(opts.input_file)

    if opts.part1:
        for i in range(0, 6):
            grid.part1_run_cycle()
            log.info("Iteration %s; %s cubes active:\n%s", i, len(grid), grid)
        result1 = len(grid)
        print(f"Part1: {result1}")

    if opts.part2:
        result2 = "TODO"
        print(f"Part2: {result2}")
