#!/usr/bin/env python3

import argparse

################################################################################

def bsearch(string, upper='B', lower='F', range_max=128):
    """Return the result of a binary search on the input string."""

    c_range = list(range(0, range_max))

    for char in string:
        c_mid = int(len(c_range) / 2)
        if char == upper:
            c_range = c_range[c_mid:]
        elif char == lower:
            c_range = c_range[:c_mid]
        #print(f"char = {char}, c_mid = {c_mid}, c_range = {c_range}")

    #print (f"end: {c_range}")
    return c_range[0]

################################################################################

def calculate_seatid(boarding):
    """
    Take an input boarding pass and output the unique seat ID.

    The boarding pass contains a string of 10 characters in the format
    'XXXXXXXYYY', where each 'X' is either 'F' or 'B', and each 'Y' is either
    'L' or 'R'.
    """

    #print (f"checking {boarding}")

    # slice the string into the requisite parts.
    row     = bsearch(boarding[:7])
    column  = bsearch(boarding[7:], upper='R', lower='L', range_max=8)

    #print(f"row = {row}, column = {column}")

    return (row * 8) + column

################################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find the numbers and return the multiple."
    )

    parser.add_argument('filename')

    opts = parser.parse_args()

    seats = []

    with open(opts.filename, 'r') as f:
        for line in f:
            # strip the newline off the end of the line.
            line = line.replace('\n', '')
            seats.append(calculate_seatid(line))

    # Sort the new list of seats.
    seats.sort()

    # Get the highest value seat in the list.
    print (f"The highest value seat is {seats[-1]}")
