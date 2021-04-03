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

def group_total_v2(group):
    """
    For an input 'group', return the number of questions they answered yes on.
    """

    ret = None

    #print (f"GROUP:\n{group}")

    for p in group:
        person = list(p)
        #person.sort()
        #print (f"loop2 {len(person)} {person}")

        if ret == None:
            ret = person
        else:
            ret = [c for c in person if c in ret]
        #ret.sort()
        #print (f"loop1 {len(ret)} {ret}")

    return len(ret)

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

def read_groups_v2(filename):
    """
    Read a file containing group answer information into a list of total 'yes's
    per group.

    Each person in the a group is represented by a line. The line for each
    person contains the letters (a-z) of each question they answered yes for.

    For each group, if all people in the group answered yes for a question then
    the group answers yes for that question.

    Each group is separated by a blank line.
    """
    ret = []

    with open(filename, "r") as group_file:
        c_group = None
        for line in group_file:
            if line in {"", "\n"}:
                if c_group is not None:
                    ret.append(group_total_v2(c_group))
                    c_group = None
                    continue

            if c_group == None:
                c_group = []

            # Strip newlines from the line
            line = line.replace('\n', '')
            c_group.append(line)

        if c_group is not None:
            ret.append(group_total_v2(c_group))
            c_group = None

        return ret

################################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find the number of trees that will be hit."
    )

    parser.add_argument("filename")

    opts = parser.parse_args()

    groups  = read_groups(opts.filename)

    groups2 = read_groups_v2(opts.filename)

    #print (groups)
    print (f"There are {len(groups)} groups (V1).")

    print (f"The sum of all the group totals (V1) is {sum(groups)}")

    print (f"There are {len(groups2)} groups (V2).")

    print (f"The sum of all the group totals (V2) is {sum(groups2)}")
