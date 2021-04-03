#!/usr/bin/env python3

import argparse
from collections import OrderedDict

################################################################################

def group_total(group):
    """
    For an input 'group', return the number of questions they answered yes on.
    """

    return len(OrderedDict.fromkeys(group))

################################################################################

def read_groups(filename):
    """
    Read a file containing group answer information into a list of total 'yes's
    per group.

    Each person in the a group is represented by a line. The line for each
    person contains the letters (a-z) of each question they answered yes for.

    For each group, if at least one person in the group answered yes for a
    question then the group answers yes for that question.

    Each group is separated by a blank line.
    """
    ret = []

    with open(filename, "r") as group_file:
        c_group = None
        for line in group_file:
            if line in {"", "\n"}:
                if c_group is not None:
                    ret.append(group_total(c_group))
                    c_group = None
                    continue

            if c_group == None:
                c_group = ""

            # Strip newlines from the line
            line = line.replace('\n', '')
            c_group += line

        if c_group is not None:
            ret.append(group_total(c_group))
            c_group = None

        return ret

################################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find the number of trees that will be hit."
    )

    parser.add_argument("filename")

    opts = parser.parse_args()

    groups = read_groups(opts.filename)

    #print (groups)
    print (f"there are {len(groups)} groups.")

    print (f"The sum of all the group totals is {sum(groups)}")
