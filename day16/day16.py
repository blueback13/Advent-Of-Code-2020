#!/usr/bin/env python3

import argparse
import logging
import math


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


def part1(
    rules: list[Rule], nearby_tickets: list[Ticket],
) -> tuple[int, list[Ticket]]:
    """
    Return sum of nearby tickets values that do not match any rule and list of
    valid tickets
    """
    invalid_values = []
    valid = []

    for ticket in nearby_tickets:
        new_invalid = ticket.get_invalid(rules)
        log.info("invalid values from ticket (%s): %s", ticket, new_invalid)

        if len(new_invalid) != 0:
            invalid_values.extend(new_invalid)
        else:
            valid.append(ticket)

    return (sum(invalid_values), valid)


################################################################################


def part2(
    rules: list[Rule], your_ticket: Ticket, nearby_tickets: list[Ticket],
) -> None:
    """
    Return sum of departure fields on your ticket

    Note: nearby tickets must be valid (as per part1())
    """
    ordered_rules = []
    for i in range(0, len(rules)):
        valid_rules = rules
        for ticket in nearby_tickets:
            valid_rules = [r for r in valid_rules if ticket[i] in r]
            log.debug(
                "Valid rules for field %s after applying %r: %s",
                i, ticket, valid_rules,
            )

        if len(valid_rules) == 0:
            raise RuntimeError(
                f"Unable to determine rule for field {i}!", rules,
            )
        # elif len(valid_rules) > 1:
        #     raise RuntimeError(
        #         f"To many possible rules for field {i}!", valid_rules,
        #     )

        ordered_rules.append(valid_rules)


    log.debug("Rules ordered by positions they could take: %s", ordered_rules)

    known_rules = []
    while len(known_rules) < len(rules):
        # Work out which slots we can identify the rule for.
        # Each time we identify a rule's field, we can remove it from the
        # possibilities for other fields; repeating this should leave us with
        # just one possibility for every field
        for i in range(0, len(ordered_rules)):
            possibilities = ordered_rules[i]
            if not isinstance(possibilities, list):
                # Skip this field - it's already been identified
                continue
            elif len(possibilities) > 1:
                # Skip this field - we can't identify it yet
                continue
            if len(possibilities) < 0:
                raise RuntimeError(
                    f"No remaining possible rules for field {i}!",
                    known_rules, ordered_rules,
                )

            log.info(
                "Identified only possible rule for field %s: %s",
                i, possibilities
            )
            ordered_rules[i] = possibilities[0]
            known_rules.append(ordered_rules[i])

        for i in range(0, len(ordered_rules)):
            possibilities = ordered_rules[i]
            if not isinstance(possibilities, list):
                # Skip this field - it's already been identified
                continue

            ordered_rules[i] = [
                r for r in possibilities if r not in known_rules
            ]

    log.debug("Rules in final order: %s", ordered_rules)
    log.debug("Your ticket: %s", your_ticket)

    ticket_values = [
        your_ticket[i] for i in range(0, len(ordered_rules))
        if ordered_rules[i].name.startswith("departure")
    ]

    log.debug(
        "Values from your ticket in 'departure' fields: %s", ticket_values,
    )

    return math.prod(ticket_values)


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

    # We need the valid tickets for part 2, so we always do this calculation
    result1, valid = part1(rules, nearby_tickets)
    if opts.part1:
        print(f"Part1: {result1}")
        print(f"  Total valid tickets: {len(valid)}")

    if opts.part2:
        result2 = part2(rules, your_ticket, valid)
        print(f"Part2: {result2}")
