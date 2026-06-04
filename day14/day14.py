#!/usr/bin/env python3

import argparse
import logging


################################################################################


log = logging.getLogger(__name__)


################################################################################


class bitmask():
    """
    Custom bitmask

    36-digit binary value, where each digit can be '0', '1', or 'X'

    When mask is applied to an integer, digits in the integer are overridden
    such that:
    - Every digit in the int that lines up with a '0' or '1' in the mask is
      replaced with the value from the mask
    - Every digit in the int that lines up with an 'X' in the mask is passed
      through unchanged
    """
    def __init__(self, mask: str = None, length: int = 36) -> None:
        """
        Set the mask

        If no mask is provided, create a default mask of all X of 'length'
        """
        if mask:
            self._mask = mask.upper()
        else:
            self._mask = "X" * length

        # Note: Python doesn't really handle bitwise operations as well as I'd
        # like, so we have to do them manually
        #
        # In other languages we could create two masks out of the bitmask:
        # 1. Applied with bitwise OR; contains all 0's except where there's
        #    a 1 in the bitmask
        # 2. Applied with bitwise AND; contains all 1's except where there's a 0
        #    in the bitmask
        self._replacements = {
            i: v
            for i, v in enumerate(self._mask)
            if v != "X"
        }

    def __repr__(self) -> str:
        return f"""bitmask(mask="{self._mask}")"""

    def apply(self, other: int) -> int:
        binary = f"{other:0{len(self._mask)}b}"
        # Note: we can't replace single elements of a string, so use list
        # comprehension to generate a result
        binary = "".join(
            self._replacements.get(i, v)
            for i, v in enumerate(binary)
        )

        return int(binary, base=2)


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

    #data = read_input(opts.input_file)

    if opts.part1:
        result1 = "TODO"
        print(f"Part1: {result1}")

    if opts.part2:
        result2 = "TODO"
        print(f"Part2: {result2}")

