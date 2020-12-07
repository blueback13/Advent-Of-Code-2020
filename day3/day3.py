#!/usr/bin/env python3

import argparse
import copy

################################################################################

def read_map(filename):
    in_map = []

    with open(filename, 'r') as f:
        for line in f:
            in_map.append(list(line.strip()))

    return in_map

################################################################################

def get_trees(in_map):
    """
    For a given map, return the number of trees that will be hit on the way to
    the bottom.

    The slope starts at the top left corner, and follows a slope of right 3
    spaces and down one space. Additionally, the map repeats infinitely off to
    the right.

    in_map - a list of strings, with each string representing a level on the
             map.
    """
    pos = 0 # starting from the top left corner.
    trees = 0

    for level in in_map:
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

def get_trees_v2(in_map, right=3, down=1):
    """
    For a given map and slope, return the number of trees that will be hit on
    the way to the bottom.

    The path down the map starts at the top left corner, and follows a map
    of right 'right' spaces and down 'down' spaces. Additionally, the map
    repeats infinitely off to the right.

    in_map - a list of strings, with each string representing a level on the
             map.
    right  - The number of spaces to move to the right per iteration.
    down   - The number of rows to move down per iteration.
    """
    pos = 0 # starting from the top left corner.
    trees = 0

    # The notation 'N:M:O' in  a list means give the elments from N  to M with a
    # step of O.
    for level in in_map[::down]:
        if level[pos] == '#':
            trees += 1
            level[pos] = 'X'
        else:
            level[pos] = 'O'
        pos += right
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

    in_map = read_map(opts.filename)
    trees = []

    slopes = [
        (1, 1),
        (3, 1),
        (5, 1),
        (7, 1),
        (1, 2),
    ]

    for slope in slopes:
        new_map = copy.deepcopy(in_map)
        new_trees = get_trees_v2(new_map, right=slope[0], down=slope[1])
        trees.append(new_trees)

        print("For slope {}, {}:".format(slope[0], slope[1]))
        for line in new_map:
            print("".join(line))

        print("There were {} trees on the slope.".format(new_trees))

    print ("Trees hit for each slope: {}".format(trees))

    total = 1
    for tree in trees:
        total *= tree
    print ("This results in a value of: {}".format(total))
