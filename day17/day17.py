#!/usr/bin/env python3

import argparse
import collections
import copy
import enum
import functools
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


@functools.lru_cache
def generate_relative_surrounding(dimensions: int = 3) -> list[tuple]:
    """Return a list of the relative positions of all neighbouring points"""
    ret = [ [] ]
    for d in range(0, dimensions):
        new_ret = []
        for i in range(-1, 2):
            # Create a new copy of every existing list for each relative offset
            new = copy.deepcopy(ret)
            for n in new:
                n.append(i)
            new_ret.extend(new)

        ret = new_ret

    ret = {tuple(v) for v in ret}

    ret.remove(tuple([0] * dimensions))

    return ret


################################################################################



class State(enum.Enum):
    """Represents the state of a point in the 3D grid"""
    active = "#"
    inactive = "."


################################################################################


def get_surrounding_points(point: tuple) -> set[tuple]:
    """Return all points that surround a given point"""
    for offset in generate_relative_surrounding(len(point)):
        yield tuple([
            x + y for x, y in zip(point, offset)
        ])


################################################################################


class Grid():
    """
    Represent a 3D grid of points, where points can be either active or inactive
    """
    def __init__(self, dimensions: int = 3, active: set[tuple] = None) -> None:
        if isinstance(active, (set, list, tuple)):
            self._active = set(active)
        elif not active:
            self._active = set()
        else:
            raise TypeError(
                "'active' must be an iterable type or ommitted; was passed an"
                f" {type(active)}", active,
            )

        self._dimensions = dimensions

        if not all([self.point_valid(p) for p in self._active]):
            raise RuntimeError(
                "Some input points are not sized correctly for an"
                f" {self.dimensions} dimensional grid",
                dimensions, active,
            )

        self._active = {tuple(p) for p in self._active}

    @classmethod
    def from_file(cls, in_file: str, dimensions: int = 3) -> typing.Self:
        """Read an input file and return a Grid"""
        newgrid = cls(dimensions=dimensions)
        # Default the value for every other dimension to 0
        # Remember the input file always has z=0 (and w=0 for part 2)
        other_defaults = [0] * (dimensions-2)

        with open(in_file) as fh:
            y = 0
            for line in fh:
                x = 0
                for value in line.strip():
                    point = (x, y, *other_defaults)
                    value = State(value)
                    log.debug("Setting point %s to %s", point, value)
                    newgrid[point] = value
                    x += 1
                y += 1

        return newgrid

    @property
    def dimensions(self) -> int:
        """Return the number of dimensions on this grid"""
        return self._dimensions

    def point_valid(self, point: tuple) -> bool:
        """
        Return True if point is valid for this grid

        In other words, the point has the right number of dimensions for this
        grid
        """
        return len(point) == self.dimensions

    def raise_point_invalid(self, point: tuple) -> None:
        """Raise a value error if point is sized incorrectly"""
        if not self.point_valid(point):
            raise ValueError(
                f"Input point is not sized correctly for an {self.dimensions}"
                " dimensional grid!",
                point,
            )

    def __getitem__(self, point: tuple) -> State:
        """Return the current state of a point"""
        self.raise_point_invalid(point)
        return State.active if point in self._active else State.inactive

    def __iter__(self) -> set[tuple]:
        """Iterate over all active points"""
        for point in self._active:
            yield point

    def __len__(self) -> int:
        """Return number of active points"""
        return len(self._active)

    def __repr__(self) -> str:
        return f"Grid(active={self._active})"

    def __str__(self) -> str:
        # Names of dimensions past x and y
        dimension_names = ["z", "w"]

        # Calculate the min and max values we need to consider in all dimensions
        minimum = [0] * self.dimensions
        maximum = [0] * self.dimensions
        for point in self:
            for d in range(0, self.dimensions):
                minimum[d] = point[d] if point[d] < minimum[d] else minimum[d]
                maximum[d] = point[d] if point[d] > maximum[d] else maximum[d]

        layer_positions = [ [] ]
        for d in range(2, self.dimensions):
            new = []
            for v in range(minimum[d], maximum[d]+1):
                new_positions = copy.deepcopy(layer_positions)
                for n in new_positions:
                    n.append(v)
                new.extend(new_positions)

            layer_positions = new

        del new, new_positions

        # Now that we have the ranges and the z(/w) coordinates we need we can
        # generate the grid
        layers = []
        for positions in layer_positions:
            rows = []
            for y in range(minimum[1], maximum[1]+1):
                rows.append(
                    "".join([
                        self[tuple([x, y, *positions])].value
                        for x in range(minimum[0], maximum[0]+1)
                    ])
                )
            layer_name = ",".join([
                (
                    dimension_names[i]
                    if i < len(dimension_names)
                    else f"dimension({i+2})"
                ) + f"={positions[i]}"
                for i in range(0, len(positions))
            ])
            layers.append(layer_name +"\n" + "\n".join(rows))

        return "\n\n".join([
            f"{layer}"
            for layer in layers
        ])

    def is_active(self, point: tuple) -> bool:
        """Return True if point is active"""
        self.raise_point_invalid(point)
        return self[point] == State.active

    def set_active(self, point: tuple) -> None:
        """Set 'point' to be active"""
        self.raise_point_invalid(point)
        self._active.add(point)

    def set_inactive(self, point: tuple) -> None:
        """Set 'point' to be inactive"""
        self.raise_point_invalid(point)
        try:
            self._active.remove(point)
        except KeyError:
            log.debug("Point %s was already inactive", point)

    def __setitem__(self, point: tuple, value: State):
        """Set 'point' to be active or inactive"""
        self.raise_point_invalid(point)
        if not isinstance(value, State):
            raise TypeError(
                f"'value' must be a 'State' object (currently {type(value)})",
                point, value,
            )
        if value == State.active:
            self.set_active(point)
        else:
            self.set_inactive(point)

    def run_cycle(self) -> None:
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

    if opts.part1:
        grid1 = Grid.from_file(opts.input_file)

        for i in range(0, 6):
            grid1.run_cycle()
            log.info("Iteration %s; %s cubes active:\n%s", i, len(grid1), grid1)
        result1 = len(grid1)
        print(f"Part1: {result1}")

    if opts.part2:
        grid2 = Grid.from_file(opts.input_file, dimensions=4)

        for i in range(0, 6):
            grid2.run_cycle()
            log.info("Iteration %s; %s cubes active:\n%s", i, len(grid2), grid2)
        result2 = len(grid2)
        print(f"Part2: {result2}")
