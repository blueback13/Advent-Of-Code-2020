#!/usr/bin/env python3

import argparse
import copy

################################################################################

def read_slope(filename):
    slope = []

    with open(filename, 'r') as f:
        for line in f:
            slope.append(list(line.strip()))

    return slope

################################################################################

def get_trees(slope):
    """
    For a given slope, return the number of trees that will be hit on the way to
    the bottom.

    The path down the slope starts at the top left corner, and follows a slope
    of right 3 spaces and down one space. Additionally, the slope repeats
    infinitely off to the right.

    slope - a list of strings, with each string representing a level on the
            slope.
    """
    pos = 0 # starting from the top left corner.
    trees = 0

    for level in slope:
        if level[pos] == '#':
            trees += 1
            level[pos] = 'X'
        else:
            level[pos] = 'O'
        pos += 3
        if not pos < len(level):
            # If the length of a line is 11, then we want to consider position
            # 12 (11 when 0-indexed, as is the case here) to be equivalent to
            # position 0 when we wrap pos back to the start. Thus we must
            # subtract the length of the line to properly wrap pos.
            pos -= len(level)

    return trees

################################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find the number of trees that will be hit."
    )

    parser.add_argument('filename')

    opts = parser.parse_args()

    slope = read_slope(opts.filename)

    slope1 = copy.deepcopy(slope)

    trees = get_trees(slope1)

    for line in slope1:
        print("".join(line))

    print("There were {} trees on the slope.".format(trees))
