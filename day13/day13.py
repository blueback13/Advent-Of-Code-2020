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
    """Solve part 2"""
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
    #
    # For example, the matrix form for 4 busses with IDs 10, x, 4, and 7 would be:
    # [ 10,  0,  0,  0, -1,  0 ]
    # [  0,  0,  4,  0, -1,  2 ]
    # [  0,  0,  0,  7, -1,  3 ]

    # id   : The bus ID (/ schedule)
    # index: The bus's index in the list
    #        (conveniently, this is also the amount to add to N for this bus)
    Constraint = collections.namedtuple("Constraint", ["id", "index"])

    constraints = [
        Constraint(id=b.id, index=i)
        for i, b in enumerate(busses)
        if not b.is_x
    ]

    # N is guaranteed to be less than or equal to the product of all bus IDs
    # Note: The product of all bus IDs does not meet the constraints itself
    upper_bound = math.prod([c.id for c in constraints])

    # Sort the constraints
    constraints = sorted(constraints, key=lambda c: c.id)

    # Find a lower bound by dividing the upper bound by the smallest constraint
    # This isn't accurate by any means, but it does cut off quite a bit of
    # search space
    lower_bound = upper_bound / constraints[0].id

    # Calculate a step
    # This is a value BX such that:
    #   BX * Y = N + I
    #   (For some value of Y and I)
    #
    # In theory we could simply take the constraint with the largest ID and use
    # it as the step, which works for all example input, but leaves to much
    # search space for the real input
    # More interestingly, if we have a value I that we know two Busses B1 and B2
    # depart at (e.g. B1 leaves B1 minutes after I and B2 leaves B2 minutes
    # after) then:
    #   B1 * B2 * Y = N + I
    # This means we can use B1 * B2 as our step; this is likely to be much
    # larger step than using an single bus, which dramatically reduces the
    # search space.
    step_constraints = [ c for c in constraints ]
    step_constraints.extend([
        Constraint(
            index=i,
            id=math.prod([b.id for b in constraints if abs(b.index - i) == b.id]),
        )
        for i in range(0, len(busses))
    ])
    step_constraints = sorted(step_constraints, key=lambda c: c.id)

    log.debug("Calculated extra constraints: %s", step_constraints)

    # Find the constraint with the biggest bus ID and use that as the step
    # This means that we don't have to try as many values to find the answer
    step = step_constraints[-1]

    # This is Y in the above equation
    # Use the lower bound to jump Y up to a value closer to the true value
    current_multiplier = int(lower_bound / step.id)

    while True:
        # N = ( B * Y ) - I
        possible_N = (step.id * current_multiplier) - step.index

        log.info(
            "Trying possible_N=%s (current_multiplier=%s; step=%s;"
            " upper_bound=%s)",
            possible_N, current_multiplier, step, upper_bound,
        )

        # Base case - we know for a fact we've gone past the target value
        if possible_N > upper_bound:
            raise RuntimeError(
                "Failed to find N for constraints!",
                constraints,
                f"upper_bound={upper_bound}",
                f"possible_N={possible_N}",
            )

        # Check if value meets all constraints
        # Y = ( N + I ) / B
        modulos = [
            ( possible_N + c.index ) % c.id
            for c in constraints
        ]

        log.debug("Modulos for N=%s: %s", possible_N, modulos)

        if all([x == 0 for x in modulos]):
            if log.level >= logging.INFO:
                multipliers = [
                    ( possible_N + c.index ) / c.id
                    for c in constraints
                ]
                log.info(
                    "Found a valid result: N=%s (constraints=%s)",
                    possible_N,
                    [
                        f"= ( {c.id} * {m} ) + {c.index}"
                        for m, c in zip(multipliers, constraints)
                    ]
                )
            return possible_N

        current_multiplier += 1


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

