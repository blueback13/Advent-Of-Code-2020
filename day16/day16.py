#!/usr/bin/env python3

import argparse
import logging


################################################################################


log = logging.getLogger(__name__)


################################################################################


class Rule():
    """A rule for a ticket field"""

    def __init__(self, spec: str) -> None:
        log.debug("Creating rule from spec: %r", spec)

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
                    self._ranges.append(range(int(top), int(bottom)+1))
                case [ OR ] if OR.lower() == "or":
                    # This condition is valid, so do nothing
                    pass
                case _:
                    raise ValueError("Invalid operation!", condition, spec)

    def __contains__(self, key: int) -> bool:
        """Return True if this rule includes 'key'"""
        for r in self._ranges:
            if key in r:
                log.debug("value %s is in range %s", key, r)
                return True

        log.debug("value %s is not in any range %r", key, self)
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

        log.debug("Creating ticket with values: %s (spec=%r)", values, spec)

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

    def get_invalid(self, rules: list[Rule]) -> list[int]:
        """Return a list of values from the ticket that do not match any of the input rules"""
        return [
            n for n in self._values
            if not any([n in r for r in rules])
        ]


################################################################################


def part1(rules: list[Rule], nearby_tickets: list[Ticket]) -> int:
    """Return sum of values from nearby tickets that do not match any rule"""
    invalid = []

    for ticket in nearby_tickets:
        new_invalid = ticket.get_invalid(rules)
        log.info("invalid values from ticket (%s): %s", ticket, new_invalid)

        invalid.extend(new_invalid)

    return sum(invalid)


################################################################################


def read_input(
    in_file: str,
) -> tuple[list[Rule], Ticket, list[Ticket]]:
    """Return rules, your ticket, and other tickets from the input"""
    rules = []
    your_ticket = None
    tickets = []

    with open(in_file) as fh:
        while True:
            line = fh.readline().strip()
            if line == "":
                break
            rules.append(Rule(line))

        if fh.readline().strip() != "your ticket:":
            raise RuntimeError(
                "Input file had unexpected order! (Expected 'your ticket:'"
            )

        your_ticket = Ticket(spec=fh.readline().strip())

        if fh.readline().strip() != "":
            raise RuntimeError(
                "Input file had unexpected order! (expected blank line)"
            )
        if fh.readline().strip() != "nearby tickets:":
            raise RuntimeError(
                "Input file had unexpected order! (expected 'nearby tickets:')"
            )

        while True:
            line = fh.readline().strip()
            if line == "":
                break
            tickets.append(Ticket(spec=line))

    return (rules, your_ticket, tickets)


################################################################################


def print_input(
    rules: list[Rule], your_ticket: Ticket, nearby_tickets: list[Ticket],
) -> None:
    for rule in rules:
        print(rule)

    print(f"\nyour ticket:\n{your_ticket}\n")

    for ticket in nearby_tickets:
        print(ticket)


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

    rules, your_ticket, nearby_tickets = read_input(opts.input_file)

    print_input(rules, your_ticket, nearby_tickets)

    if opts.part1:
        result1 = part1(rules, nearby_tickets)
        print(f"Part1: {result1}")

    if opts.part2:
        result2 = "TODO"
        print(f"Part2: {result2}")


