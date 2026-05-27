#!/usr/bin/env python3

import argparse
import bisect
import logging


################################################################################


log = logging.getLogger(__name__)


################################################################################


class XMAS():
    """
    eXchange-Masking Addition System (XMAS) data to be attacked

    Arguments:
      *args  : Raw XMAS data (only used when in_file is not provided)
      in_file: Path to file containing XMAS data
    """

    _preamble_length = 25

    def __init__(self, *args, in_file=None):
        """Initialise XMAS data from file OR from arguments"""
        self._data = []

        if in_file is not None:
            self.parse_input(in_file)
        else:
            for arg in args:
                self._data.append(int(arg))

    def parse_input(self, in_file) -> None:
        """Parse an input file into XMAS data"""
        if len(self._data) > 0:
            raise RuntimeError("XMAS data already initialised!", in_file, self)

        with open(in_file) as fh:
            for line in fh:
                self._data.append(int(line))

    def get_preamble(self) -> list[int]:
        """
        Return the XMAX preamble

        This is the first 25 elements of the list
        """
        return self._data[:self._preamble_length]

    def get_first_index(self) -> int:
        """Return first non-preamble index"""
        return self._preamble_length

    def __getitem__(self, item) -> int:
        """Return list element at index 'item'"""
        return self._data[item]

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"XMAS({ ', '.join(str(n) for n in self._data) })"


################################################################################


def find_first_invalid(data: XMAS) -> int:
    """
    Return the index of the first invalid XMAS data value

    A data value is invalid if it does not follow the following rule:
      Each value must be a sum of any two of the proceeding 25 values
    (The first 25 values are excluded from this rule - they form the 'preamble')

    Arguments:
      data: XMAS data
    """
    def is_valid(value, last_n) -> bool:
        """
        Return True if value follows the rule

        last_n _must_ be sorted!
        """
        log.info("Testing validity of value %s (last_n=%s)", value, last_n)

        lower = 0
        upper = len(last_n) - 1

        while upper > lower:
            log.debug("Loop iteration: ", )
            l = last_n[lower]
            u = last_n[upper]
            s = l + u
            log.debug(
                "is_valid(): iteration: lower=%s (l=%s); upper=%s (u=%s), s=%s; value=%s",
                lower, l, upper, u, s, value
            )
            if s == value:
                log.info("value %s is valid! (%s + %s)", value, l, u)
                return True
            elif s > value:
                upper -= 1
            else:
                lower += 1

        log.info("Value %s is invalid!", value)
        return False

    min_valid_index = 0
    current_index = data.get_first_index()

    last_n_sorted = sorted(data.get_preamble())

    log.debug("Pre-loop: current_index=%s; len(data)=%s", current_index, len(data))

    while current_index < len(data):
        log.debug("Main loop iteration: current_index=%s; len(data)=%s", current_index, len(data))

        current_value = data[current_index]
        if not is_valid(current_value, last_n_sorted):
            log.info(
                "Found first invalid value! (value %s at index %s)",
                current_value, current_index
            )
            return current_index

        # Set up for next iteration

        # Remove oldest value from the list and increase the min valid index
        last_n_sorted.remove(data[min_valid_index])
        min_valid_index += 1

        # Add the current value to the list
        bisect.insort(last_n_sorted, current_value)

        # Increment the current index
        current_index +=1

    # Note: It's possible to reach this point with well-formed data, but
    # shouldn't be possible based on the rules of the challenge
    log.warning("FAILED TO FILE AN INVALID VALUE FOR DATA! (%s)", data)
    return None


################################################################################


def get_weakness_range(data: XMAS, target: int) -> tuple[int, int]:
    """
    Return first and last indexes of range that sums to 'target'

    Arguments:
      data  : XMAS data
      target: First value that was invalid
    """

    log.info("Searching for continuous range with sum=%s (%s)", target, data)

    bot_index = 0

    while bot_index < len(data) - 1:
        log.info("Testing range starting with index %s", bot_index)

        # start summing
        current_total = data[bot_index]

        top_index = bot_index + 1

        while current_total < target:
            current_total += data[top_index]

            log.debug(
                "Iteration: current_total=%s; start=%s; end=%s",
                current_total, bot_index, top_index
            )

            if current_total == target:
                log.info(
                    "Found range that sums to %s! - start=%s; end=%s; range=%s",
                    target, bot_index, top_index, data[bot_index:top_index+1]
                )
                return (bot_index, top_index)

            # Setup for next iteration
            top_index += 1

        bot_index += 1

    log.warning("Could not find a range that summed to %s (%s)", target, data)
    return None


################################################################################


if __name__ == "__main__":
    logging.basicConfig()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(
        description="Decipher and attack XMAS data"
    )

    parser.add_argument("input_file")

    opts = parser.parse_args()

    data = XMAS(in_file=opts.input_file)

    log.info("Parsed input: %s", data)

    first_invalid_index = find_first_invalid(data)
    first_invalid = data[first_invalid_index]
    print(f"Part 1: {first_invalid}")
    print(f"  Found at index {first_invalid_index}")

    start, end = get_weakness_range(data, first_invalid)
    part2 = data[start] + data[end]
    print(f"Part 2: {part2}")
    print(f"  range start={start}; end={end}; range={data[start:end+1]}")
