#!/usr/bin/env python3

import argparse

################################################################################

# Copied from
# https://stackoverflow.com/questions/5764782/iterate-through-pairs-of-items-in-a-python-list
def pairs(seq):
    i = iter(seq)
    prev = next(i)
    for item in i:
        yield prev, item
        prev = item

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

    ##### Part 2 #####

    # Find a seats that are missing from the list.
    for p, n in pairs(seats):
        #print (f"p = {p}, n = {n}")
        if (n - p) != 1:
            missing = p + 1
            print(f"Looks like {missing} is missing (p = {p}, n = {n})")
