#!/usr/bin/env python3

import argparse
import collections
import logging
import math


################################################################################


log = logging.getLogger(__name__)

Bus = collections.namedtuple("bus", ["is_x", "id"])


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
        log.error("Not yet implemented")

