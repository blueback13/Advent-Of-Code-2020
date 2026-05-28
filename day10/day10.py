#!/usr/bin/env python3

import argparse
import logging


################################################################################


log = logging.getLogger(__name__)


################################################################################


def read_file(path: str) -> list[int]:
    """
    Return the adaptor joltages form file at 'path'
    """
    ret = []
    with open(path) as fh:
        for line in fh:
            ret.append(int(line))

    return ret


################################################################################


def part1(data: list[int]) -> int:
    """
    Construct adaptor chain and count number of 1 and 3 jolt differences
    Return number of 1-jolt differences times the number of 3-jolt differences
    """
    log.info("Constructing chain using adaptors: %s", data)

    # Note - so far as I can tell simply sorting the input list is enough to
    # construct a chain using all adaptors
    chain = sorted(data)

    # Add device's built-in adaptor and the outlet's joltage
    chain = [0] + chain + [chain[-1] + 3]

    log.info("Calculated chain: %s", chain)

    # Calculate joltage differences
    differences = [m - n for n, m in zip(chain[:-1], chain[1:])]
    log.debug("Calculated differences: %s", differences)

    counts = {}
    for diff in differences:
        counts[diff] = counts.get(diff, 0) + 1

    log.debug("Difference counts: %s", counts)

    return counts.get(1, 0) * counts.get(3, 0)


################################################################################


if __name__ == "__main__":
    logging.basicConfig()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(
        description="Calculate joltage differences"
    )

    parser.add_argument("input_file")

    opts = parser.parse_args()

    data = read_file(path=opts.input_file)

    log.debug(f"Input: {data}")

    result1 = part1(data)
    print(f"Part 1: {result1}")
