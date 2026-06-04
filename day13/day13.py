#!/usr/bin/env python3

import argparse
import collections
import logging
import math


################################################################################


log = logging.getLogger(__name__)

Bus = collections.namedtuple("Bus", ["is_x", "id"])


################################################################################


def part1(current_time: int, busses: list[Bus]) -> tuple[int, int]:
    """Return ID of the next bus and the number of minutes we need to wait"""
    # Calculate the next departure time for all busses that aren't x's
    #
    # Given bus B and current time T, say the next departure time is N
    # We know that:
    #   T / B < N / B
    # And, since N is the next possible departure after T, we know that:
    #   (N / B) - (T / B) < 1
    # Given this, we can find N using the formula:
    #   ceiling( T / B ) * B = N
    times = [
        (math.ceil(current_time / b.id) * b.id, b.id)
        for b in busses
        if not b.is_x
    ]

    times = sorted(times, key=lambda x: x[0])

    departure_time, bus_id = times[0]
    wait = departure_time - current_time
    log.debug(
        "Best bus at %s is %s, departing next at %s (in %s minutes)",
        current_time, bus_id, departure_time, wait,
    )

    return bus_id, wait


################################################################################


def part2(busses: list[Bus]) -> int:
    """
    Solve part 2

    Note: I got a tip from Reddit on how to implement this solution:
    https://old.reddit.com/r/adventofcode/comments/kc60ri/2020_day_13_can_anyone_give_me_a_hint_for_part_2/gfnnfm3/
    """
    # Each bus becomes a new constraint on the system
    # Say N is the unknown we want to find.
    # The Ith Bus (0-indexed) with ID B applies constraint:
    #   B * Y = N + I
    # (Where Y is the number of bus iterations needed)
    # We can restate this as:
    #  B * Y - N = I
    # This allows us to state the problem as a system of such equations, which
    # can be solved for the unknowns.
    #
    # Also, bus I is skipped if the bus's ID is 'x'

    # id   : The bus ID (/ schedule)
    # index: The bus's index in the list
    #        (conveniently, this is also the amount to add to N for this bus)
    Constraint = collections.namedtuple("Constraint", ["id", "index"])

    # Enumerate the input busses to generate the constraints array
    constraints = [
        Constraint(id=b.id, index=i)
        for i, b in enumerate(busses)
        if not b.is_x
    ]

    # Sort the constraints
    constraints = sorted(constraints, key=lambda c: c.id)

    # Initial value for N; e.g. a value of N that is valid for the first
    # constraint alone.
    # For a single constraint Y=1, so we can find N for a single constraint:
    #   N = B - I
    possible_N = constraints[0].id - constraints[0].index

    # The first bus B comes every B minutes - use that as the step size
    step = constraints[0].id

    # repeatedly find N for first X busses until all busses have been included
    for i in range(2, len(constraints)+1):
        log.info(
            "Calculating N for first %s constraints (step=%s; constraints=%s)",
            i, step, constraints[:i],
        )

        while True:
            # Check if current N meets all constraints
            # Y = ( N + I ) / B
            modulos = [
                ( possible_N + constraints[j].index ) % constraints[j].id
                for j in range(0, i)
            ]
            log.debug(
                "Modulos for first %s constraints when N=%s: %s",
                i, possible_N, modulos,
            )
            if all([x == 0 for x in modulos]):
                log.info(
                    "Found result for first %s constraints: N=%s",
                    i, possible_N,
                )
                # Step for the next iteration is the product of the current step
                # and the constraint that we added this iteration
                step *= constraints[i-1].id
                break

            possible_N += step

        log.info(
            "Iteration complete; for first %s constraints N=%s",
            i, possible_N,
        )

    log.info("Calculated final N=%s", possible_N)

    if log.level >= logging.DEBUG:
        multipliers = [
            ( possible_N + c.index ) / c.id
            for c in constraints
        ]
        log.debug(
            "Constraints for N=%s: %s",
            possible_N,
            [
                f"= ( {c.id} * {m} ) + {c.index}"
                for m, c in zip(multipliers, constraints)
            ],
        )

    return possible_N


################################################################################


def read_input(in_file: str) -> tuple[int, list[Bus]]:
    """
    Return current time and list of bus IDs
    """
    with open(in_file) as fh:
        current_time = int(fh.readline().strip())
        bus_ids = fh.readline().strip()

    busses = [
        Bus(b == "x", b if b == "x" else int(b))
        for b in bus_ids.split(",")
    ]

    return (current_time, busses)


################################################################################


if __name__ == "__main__":
    logging.basicConfig()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(
        description="Bus timetable reader"
    )

    parser.add_argument("input_file")
    parser.add_argument("--part1", action=argparse.BooleanOptionalAction)
    parser.add_argument("--part2", action=argparse.BooleanOptionalAction)

    opts = parser.parse_args()

    current_time, busses = read_input(opts.input_file)

    if opts.part1:
        bus_id, wait = part1(current_time, busses)
        result1 = bus_id * wait
        print(f"Part1: {result1}")

    if opts.part2:
        N = part2(busses)
        print(f"Part2: {N}")

