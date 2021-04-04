#!/usr/bin/env python3

import argparse

################################################################################

def get_colour(bag):
    return bag.replace(' bags', '').replace(' bag', '')

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

    def __repr__(self):
        return (
            f"{self.__class__.__name__}{{colour='{self.colour}', "
            + f"contains='{self.contains}', contained='{self.contained}'}}"
        )

################################################################################

class baglist:
    """
    This class contains a list of all bags, and methods for getting information
    about the bag list.
    """

    def __init__(self):
        self._bags = {}

    def add_bag(self, colour, contains=None):
        newbag = self._bags.get(colour)
        if newbag is None:
            self._bags[colour] = bag(colour, contains=contains)
        else:
            newbag.contains = contains

        for b in contains:
            somebag = self._bags.get(b)
            if somebag is None:
                #print (f"{colour}: adding {b}")
                self._bags[b] = bag(b, contained=[colour])
            else:
                #print (f"{colour}: {b}")
                somebag.contained.append(colour)

    def parse_bag(self, baginfo):
        """Return a bag object from a description of a bag 'baginfo'."""

        # strip the newline off the end of the line.
        baginfo = baginfo.replace('\n', '')
        baginfo = baginfo.replace('.', '')

        main, inner = baginfo.split("contain", 1)

        contains = inner.split(',')

        main = get_colour(main.strip())
        contains = [(get_colour(c.strip())).split(" ", 1)[1] for c in contains]

        #print (f"main='{main}', inner='{inner}', contains='{contains}'")

        self.add_bag(main, contains)

    def read_file(self, filename):
        with open(filename, "r") as f:
            for line in f:
                self.parse_bag(line)

    def __repr__(self):
        return (f"{self.__class__.__name__}{{_bags='{self._bags}'}}")

    def __str__(self):
        bagstring = "".join([f"\t{self._bags[bag]}\n" for bag in self._bags])
        return (f"{self.__class__.__name__}\n{{\n{bagstring}}}")

################################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find bags that can contain 'Shiny Gold' bags."
    )

    parser.add_argument('filename')

    opts = parser.parse_args()

    main_baglist = baglist()
    main_baglist.read_file(opts.filename)

    print (main_baglist)
