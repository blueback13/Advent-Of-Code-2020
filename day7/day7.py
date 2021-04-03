#!/usr/bin/env python3

import argparse

################################################################################

class bag:
    """
    This class contains the data for a bag.

    colour    - contains a string describing the colour of the bag.
    contains  - List of bags that this bag can contain.
    contained - List of bags that can contain this bag.
    """

    def __init__(self, colour, contains=None, contained=None):
        self.colour    = colour
        self.contains  = [] if contains is None else contains
        self.contained = [] if contained is None else contained

################################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find bags that can contain 'Shiny Gold' bags."
    )

    parser.add_argument('filename')

    opts = parser.parse_args()

    numbers = []
