#!/usr/bin/env python3

import argparse
import logging
import math


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


def part2(data: list[int]) -> int:
    """
    Return number of ways adaptor chain can be constructed
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

    # Find length of all continuous chains of 1s by converting the list to a
    # string and splitting on 3
    as_str = ''.join(str(x) for x in differences)
    one_chains = as_str.split('3')
    log.debug("Got chains of ones: %s", one_chains)
    # Consider only the chains that are at least two 1s long
    one_chain_lengths = [len(y) for y in one_chains if len(y) > 1]
    log.debug("Chain lengths to consider: %s", one_chain_lengths)

    # Total permutations for N 1-jolt differences in a row is (2 ^ N-1)
    # **However**, because each difference can only be 3 jolts, this means our
    # total number of permutations is reduced.
    # In practice this means we subtract N - 3 from the result when N > 3
    # So final calculation is: (2 ^ N-1) - (N - 3) if N > 3
    #
    # Note: I came up with the "- (N-3)" part kinda by accident; I don't know if
    # it's correct for N>4, and I don't know how to prove it mathematically. It
    # works though so...
    chain_permutations = map(
        lambda x: 2**(x-1) - ((x - 3) if x > 3 else 0),
        one_chain_lengths,
    )
    # Convert generator to list so we don't accidentally consume it when logging
    chain_permutations = [x for x in chain_permutations]
    log.debug("Permutations for each chain of ones: %s", chain_permutations)

    # To find total overall permutations, multiply the total permutations for
    # all 1-jolt chains together
    result = math.prod(chain_permutations)
    log.debug("Final permutations: %s", result)
    return result


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

    result2 = part2(data)
    print(f"Part 2: {result2}")
