#!/usr/bin/env python3

import argparse
import logging


################################################################################


log = logging.getLogger(__name__)


################################################################################


class Rule():
    """A rule for a ticket field"""

    def __init__(self, spec: str) -> None:
        self._name, conditions = spec.split(":")

        # The range(n, m) builtin returns a class representing a range that
        # starts at n and ends at m. This is usually used for iteration, but
        # also allows use of the 'in' operator such that:
        #   x in range(n, m) == (n <= x < m)
        # (This isn't quite what we want - we want to include 'm' in the range -
        # but the adjustment is easy enough)
        self._ranges = []

        for condition in conditions.strip().split(" "):
            match condition.split("-"):
                case [ top, bottom ]:
                    self._ranges.append(range(top, bottom+1))
                case OR if OR.lower() == "or":
                    # This condition is valid, so do nothing
                    pass
                case _:
                    raise ValueError("Invalid operation!", condition, spec)

    def __contains__(self, key: int) -> bool:
        """Return True if this rule includes 'key'"""
        for r in self._ranges:
            if key in r:
                return True

        return False

    @property
    def name(self) -> str:
        return self._name

    def __str__(self) -> str:
        rangestr = " or ".join([f"{r.start}-{r.stop-1}" for r in self._ranges])
        return f"{self._name}: {rangestr}"

    def __repr__(self) -> str:
        return f"""Rule(spec="{self}")"""


################################################################################


class Ticket():
    """
    A ticket with N fields

    Arguments:
      *values: Integers containing values for each of the ticket fields
      spec   : A string containing comma-separated values
               If spec is provided, no parameters can be passed for 'values'
    """
    def __init__(self, *values: int, spec: str = None) -> None:
        if spec is not None:
            if len(values) > 0:
                raise RuntimeError(
                    "Cannot pass both 'spec' and 'values'", values, spec,
                )

            values = spec.split(",")

        self._values = [ int(value) for value in values ]


    def __getitem__(self, key: int) -> int:
        """Return key'th value from ticket"""
        return self._values[key]

    def __iter__(self) -> list[int]:
        """Iterate over ticket values"""
        for v in self._values:
            yield v

    def __str__(self) -> str:
        """Return ticket spec (as seen in the input)"""
        return ",".join([str(v) for v in self._values])

    def __repr__(self) -> str:
        return f"""Ticket({ ", ".join([str(v) for v in self._values]) })"""

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

    if opts.part1:
        result1 = "TODO"
        print(f"Part1: {result1}")

    if opts.part2:
        result2 = "TODO"
        print(f"Part2: {result2}")


