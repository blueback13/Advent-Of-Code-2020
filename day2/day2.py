#!/usr/bin/env python3

import argparse
import types

def read_passwords(filename):
    """
    Open a file 'filename' and read the lines into a list.

    The line format is:
    L-U C: PASS
    where:
    L    - lower value in range
    U    - Upper value in range
    C    - Target character
    PASS - password
    """
    passwords = []

    with open(opts.filename, 'r') as f:
        for line in f:
            data = line.split()
            r = data[0].split('-')
            el = types.SimpleNamespace(
                lower=int(r[0]),
                upper=int(r[1]),
                char=data[1][0],
                password=data[2]
            )
            passwords.append(el)

    return passwords

def valid_passwords_v1(filename):
    """
    Return the number of valid passwords in 'filename'

    Password rule is that the number of occurrences of 'char' must lie between
    'lower' and 'upper'.
    """
    passwords = read_passwords(filename)
    valid = 0

    for p in passwords:
        total = p.password.count(p.char)
        if p.lower <= total <= p.upper:
            #print ("{} <= {} <= {}".format(p.lower, total, p.upper))
            valid += 1

    return valid

def valid_passwords_v2(filename):
    """
    Return the number of valid passwords in 'filename'

    Password rule is that 'char' must occur at EITHER 'lower' or 'upper'
    """
    passwords = read_passwords(filename)
    valid = 0

    xor = lambda a, b: (a and not b) or (not a and b)

    for p in passwords:
        # Get the chars to compare.
        # Note that the target chars are NOT 0-indexed.
        char1 = p.password[p.lower - 1]
        char2 = p.password[p.upper - 1]
        if xor((char1 == p.char),(char2 == p.char)):
            #print ("{} != {}".format(char1, char2))
            valid += 1

    return valid


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find the numbers and return the multiple."
    )

    parser.add_argument('filename')

    opts = parser.parse_args()

    #passwords = read_passwords(opts.filename)
    #for p in passwords:
    #    print (
    #        (
    #            "The range: ({}, {}) | the character: '{}' | the password: '{}'"
    #        ).format(p.lower, p.upper, p.char, p.password)
    #    )

    print("Total valid passwords V1 = {}".format(valid_passwords_v1(opts.filename)))

    print("Total valid passwords V2 = {}".format(valid_passwords_v2(opts.filename)))
