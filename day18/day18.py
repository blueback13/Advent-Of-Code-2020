#!/usr/bin/env python3

import argparse
import collections
import logging


################################################################################


log = logging.getLogger(__name__)


################################################################################


class Operator():
    """
    Base Operator

    Does nothing itself. Is only used to initialise other operators
    """
    # List of available subclass instances
    _registry = []

    @staticmethod
    def _match_op(operator: str) -> bool:
        """Return True if this subclass works on cmd"""
        raise RuntimeError("_match_command() not overridden!", cmd)

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Initialise a new command type
        """
        super().__init_subclass__(**kwargs)
        # Note: Operations have no data, so we can treat them as singletons
        cls._registry.append(cls())

    def __new__(cls, operator: str, *args, **kwargs):
        """Return an object of the appropriate subclass for input SeatState"""
        for op in cls._registry:
            if op._match_op(operator):
                return op

        if not newcls:
            raise RuntimeError("No handler for operator!", state)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        return "??"

    def __call__(self, x: int, y: int) -> int:
        """Return the result of applying this operation to x and y"""
        raise NotImplementedError("Must override operation in subclass!")


################################################################################


class Problem():
    """A math homework problem"""
    def __init__(
        self, problems: list, operators: list[Operator] = None,
    ) -> None:
        self._probs = problems
        self._ops = operators if operators is not None else []

        if not (
            isinstance(self._probs, [list, tuple])
            and all([isinstance(x, type(self)) for x in self._probs])
        ):
            raise TypeError(
                "'problems' must be a list of Problems",
                self._probs
            )
        elif not (
            isinstance(self._ops, [list, tuple])
            and all([isinstance(x, Operator) for x in self._ops])
        ):
            raise TypeError(
                "'operators' must be a list of Operators", self._ops
            )
        elif not (len(numbers) == len(operators) + 1):
            raise RuntimeError(
                "Number of operators must be 1 less than number of numbers"
                self._numbers, self._ops,
            )

    def evaluate(self) -> int:
        """Return result of evaluating the equation defined by this object"""
        pass

    def __len__(self) -> int:
        """Return number of subproblems in this problem"""
        return len(self._probs)

    def __str__(self) -> str:
        return str(self._probs[0]) + " " + " ".join([
            str(o) + " " + (f"({p})" if len(p) > 1 else str(p))
            for o, p in zip(self._ops, self._probs[1:])
        ])


################################################################################


def do_homework(problem: str) -> int:
    """
    Process a line of homework and return the result

    Remember, operator precedence doesn't exist, so calculations are performed
    blindly right-left (except when brackets change the order
    """
    pass


################################################################################


if __name__ == "__main__":
    logging.basicConfig()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(
        description="Math homework processor"
    )

    parser.add_argument("input_file")
    parser.add_argument("--part1", action=argparse.BooleanOptionalAction)
    parser.add_argument("--part2", action=argparse.BooleanOptionalAction)

    opts = parser.parse_args()

    if opts.part1:
        result1 = "TODO"
        print(f"Part1: {result1}")

    if opts.part2:
        result2 = "TODO"
        print(f"Part2: {result2}")
