#!/usr/bin/env python3

import argparse
import enum
import functools
import logging


################################################################################


log = logging.getLogger(__name__)


################################################################################


class SeatState(enum.Enum):
    """
    Possible states for a seat

    Meanings:
      occupied : Someone is sitting in the seat
      empty    : No one is sitting in the seat
      blank    : There is no seat at this location
    """
    occupied = "#"
    empty  = "L"
    blank  = "."


################################################################################


class GridSquare():
    """Representation of a grid square - either a seat or a patch of floor"""

    # Registry of SeatStates mapped to GridSquare subclasses
    _registry = {s: None for s in SeatState}

    def __init_subclass__(cls, states: list[SeatState] = None, **kwargs) -> None:
        """
        Initialise a new type of object that may occupy a grid square

        Each type of object must claim one or more SeatStates

        When creating a GridSquare, the constructor will automatically create an
        object of the registered type instead
        """
        super().__init_subclass__(**kwargs)
        if not states:
            raise RuntimeError(
                "Subclass does not claim any desired states!", cls,
            )
        elif type(states) is not list:
            raise ValueError("Subclass passed a non-list object!", cls, states)

        for state in states:
            if type(state) is not SeatState:
                raise ValueError(
                    "Subclass passed an invalid state type!", cls, state
                )
            cls._registry[state] = cls

    def __new__(cls, state: SeatState = SeatState.blank):
        """Return an object of the appropriate subclass for input SeatState"""
        newcls = cls._registry[state]
        if not newcls:
            raise RuntimeError("No handler for state!", state)

        obj = super().__new__(newcls)
        obj.__init__(state)
        return obj

    def __init__(self, state: SeatState = SeatState.blank) -> None:
        """Initialise the GridSquare's state"""
        self._state = state

    def __str__(self) -> str:
        return self._state.value

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._state})"

    @property
    def state(self) -> SeatState:
        """The current state of the GridSquare"""
        return self._state

    def change_state(self) -> None:
        """Do nothing - By default squares can't change state"""
        log.debug("GridSquare.change_state(): Not changing state")


################################################################################


class Floor(GridSquare, states=[SeatState.blank]):
    """An empty square of floor"""
    pass


################################################################################


class Seat(GridSquare, states=[SeatState.occupied, SeatState.empty]):
    """
    A seat - may be occupied or empty
    """
    def change_state(self) -> None:
        """Change an empty seat to occupied or vice-versa"""
        if self._state == SeatState.empty:
            log.debug("Seat State changing to occupied!")
            self._state = SeatState.occupied
        else:
            log.debug("Seat State changing to empty!")
            self._state = SeatState.empty


################################################################################


class SeatLayout():
    """
    Representation of a seat layout
    """
    def __init__(self, in_layout: str | list[str]) -> None:
        self._grid = []

        if type(in_layout) == str:
            log.info("Loading layout from file %s", in_layout)
            with open(in_layout) as fh:
                _input = [l.strip() for l in fh]
        else:
            log.info("Treating in_layout as direct input")
            _input = in_layout

        self._grid = [
            [GridSquare(SeatState(s)) for s in l.strip()]
            for l in _input
        ]

        if self.hight == 0:
            raise ValueError("Input layout was empty!", in_layout, _input)


    @property
    def hight(self) -> int:
        """Return vertical length of the grid"""
        return len(self._grid)

    y = hight

    @property
    def width(self) -> int:
        """Return horizontal length of the grid"""
        return len(self._grid[0])

    x = width

    @property
    def dimensions(self) -> tuple[int, int]:
        """Return dimensions of the grid (x, y)"""
        return (self.x, self.y)


    def __str__(self) -> str:
        return "\n".join(
            [
                "".join([str(s) for s in row])
                for row in self._grid
            ]
        )

    def __repr__(self) -> str:
        strings = ["".join([str(s) for s in row]) for row in self._grid]
        return f"SeatLayout({strings})"

    def is_in_bounds(self, x: int, y: int) -> bool:
        """Return true if both x and y are in bounds"""
        return (x >= 0 and x < self.width) and (y >= 0 and y < self.hight)

    def get_square(self, x: int, y: int) -> GridSquare:
        """Get square at x, y"""
        if not self.is_in_bounds(x, y):
            raise ValueError("X and Y coordinates out of bounds!", x, y)

        return self._grid[y][x]

    def count_squares(self, state: SeatState = None) -> int:
        """
        Count the number of squares in the grid

        If state is provided, count the number of squares that match the target
        state
        """
        if state:
            log.debug("Counting squares in state %s", state)
            _f = lambda s: s.state == state
        else:
            log.debug("Counting all squares")
            _f = lambda s: True

        return sum([
            sum([1 for y in range(self.hight) if _f(self.get_square(x, y))])
            for x in range(self.width)
        ])

    def get_adjacent_seats(self, x: int, y: int) -> list[GridSquare]:
        """Return list of seats adjacent to the seat at x, y"""
        positions = [
            (x - 1, y - 1), (x    , y - 1), (x + 1, y - 1),
            (x - 1, y    ),                 (x + 1, y    ),
            (x - 1, y + 1), (x    , y + 1), (x + 1, y + 1),
        ]
        ret = [
            self.get_square(nx, ny)
            for nx, ny in positions
            if self.is_in_bounds(nx, ny)
        ]
        return [s for s in ret if type(s) is Seat]

    def get_visible_seats(self, x: int, y: int) -> list[GridSquare]:
        """Return a list of seats visible to the seat at x, y"""
        directions = [
            (-1, -1), (0 , -1), (1 , -1),
            (-1, 0 ),           (1 , 0 ),
            (-1, 1 ), (0 , 1 ), (1 , 1 ),
        ]
        ret = []

        for xdiff, ydiff in directions:
            currentx = x
            currenty = y
            while True:
                currentx += xdiff
                currenty += ydiff
                try:
                    current = self.get_square(currentx, currenty)
                except ValueError:
                    break

                if type(current) is Seat:
                    ret.append(current)
                    break

        return ret

    def apply_seat_changes(self, seats = list[tuple[int, int]]) -> None:
        """Change state of seats based on listed coordinates"""
        for x, y in seats:
            self.get_square(x, y).change_state()

    def _iteration(
            self, threshold: int, method: callable
    ) -> list[tuple[int, int]]:
        """
        Return list of all seats that would change state

        Seats are returned as tuples representing the x and y positions

        Rules:
        - If a seat is empty (L) and there are no occupied seats adjacent to it,
          the seat becomes occupied.
        - If a seat is occupied (#) and four or more seats adjacent to it are
          also occupied, the seat becomes empty.
        - Otherwise, the seat's state does not change.
        """
        ret = []
        for x in range(self.width):
            for y in range(self.hight):
                current = self.get_square(x, y)
                if type(current) is Floor:
                    log.debug("Skipping square (%s, %s) - not a seat", x, y)
                    continue

                log.debug("Testing if seat at (%s, %s) will change state", x, y)
                seats = method(self, x, y)
                log.debug("Seats considered by (%s, %s): %s", x, y, seats)

                count = sum(
                    [1 for s in seats if s.state is SeatState.occupied]
                )
                if (
                        (current.state == SeatState.occupied and count >= threshold)
                        or (current.state == SeatState.empty and count == 0)
                ):
                    log.debug(
                        "Seat at (%s, %s) will change state (%s considered"
                        " seats occupied; threshold %s; seat currently %s)",
                        x, y, count, threshold, current.state
                    )
                    ret.append((x, y))
                else:
                    log.debug(
                        "Seat at (%s, %s) will not change state (%s considered"
                        " seats occupied; threshold %s; seat currently %s)",
                        x, y, count, threshold, current.state
                    )

        log.debug("Seats that will change state: %s", ret)

        return ret

    def run_simulation(
            self, threshold: int = 4, method: callable = get_adjacent_seats
    ) -> int:
        """Return the number of occupied seats after the iterations stabilise"""
        while True:
            log.debug("State at iteration start:\n%s", self)

            changing = self._iteration(threshold, method)
            if len(changing) == 0:
                log.info("Arrived at final state!")
                break
            self.apply_seat_changes(changing)

        log.debug("Final state:\n%s", self)
        return self.count_squares(state=SeatState.occupied)

    part1 = functools.partialmethod(run_simulation)

    part2 = functools.partialmethod(
        run_simulation, threshold=5, method=get_visible_seats
    )

################################################################################


if __name__ == "__main__":
    logging.basicConfig()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(
        description="Airport seat simulator"
    )

    parser.add_argument("input_file")
    parser.add_argument("--part1", action=argparse.BooleanOptionalAction)
    parser.add_argument("--part2", action=argparse.BooleanOptionalAction)

    opts = parser.parse_args()

    if opts.part1:
        grid1 = SeatLayout(in_layout=opts.input_file)

        part1_result = grid1.part1()
        print(f"Part 1: {part1_result}")

    if opts.part2:
        grid2 = SeatLayout(in_layout=opts.input_file)

        part2_result = grid2.part2()
        print(f"Part 2: {part2_result}")
