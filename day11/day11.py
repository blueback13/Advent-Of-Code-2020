#!/usr/bin/env python3

import argparse
import enum
import logging


################################################################################


log = logging.getLogger(__name__)


################################################################################


class SeatState(enum.Enum):
    """
    Possible states for a seat

    Meanings:
      filled : Someone is sitting in the seat
      empty  : No one is sitting in the seat
      blank  : There is no seat at this location
    """
    filled = "#"
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
        log.info("GridSquare.change_state(): Not changing state")


################################################################################


class Floor(GridSquare, states=[SeatState.blank]):
    """An empty square of floor"""
    pass


################################################################################


class Seat(GridSquare, states=[SeatState.filled, SeatState.empty]):
    """
    A seat - may be filled or empty
    """
    def change_state(self) -> None:
        """Change an empty seat to filled or vice-versa"""
        if self._state == SeatState.empty:
            self._state = SeatState.filled
        else:
            self._state == SeatState.empty


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

################################################################################


if __name__ == "__main__":
    logging.basicConfig()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(
        description="Airport seat simulator"
    )

    parser.add_argument("input_file")

    opts = parser.parse_args()

    grid = SeatLayout(in_layout=opts.input_file)

    print(repr(grid))

