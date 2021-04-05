#!/usr/bin/env python3

import argparse
from queue import Queue

################################################################################

def get_colour(bag):
    return bag.replace(' bags', '').replace(' bag', '')

################################################################################

class Bag:
    """
    This class contains the data for a bag.

    colour    - contains a string describing the colour of the bag.
    contains  - List of bags that this bag can contain.
    contained - List of bags that can contain this bag.
    """

    def __init__(self, colour, contains=None, contained=None):
        self.colour    = colour
        self.contains  = {} if contains is None else contains
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
        """
        Add a Bag 'colour' to the list of all bags.

        Note that if the bag already exists in the list of bags then the list of
        bags it can contain will be updated in place instead.
        """

        newbag = self._bags.get(colour)
        if newbag is None:
            self._bags[colour] = Bag(colour, contains=contains)
        else:
            newbag.contains = contains

        for b in contains:
            somebag = self._bags.get(b)
            if somebag is None:
                #print (f"{colour}: adding {b}")
                self._bags[b] = Bag(b, contained=[colour])
            else:
                #print (f"{colour}: {b}")
                somebag.contained.append(colour)

    def parse_bag(self, baginfo):
        """Return a bag object from a description of a bag 'baginfo'."""

        # strip the newline off the end of the line.
        baginfo = baginfo.replace('\n', '')
        baginfo = baginfo.replace('.', '')

        main, inner = baginfo.split("contain", 1)

        main = get_colour(main.strip())

        contains = {}

        if inner.strip() != "no other bags":
            for c in inner.split(','):
                pair = (get_colour(c.strip())).split(" ", 1)
                contains[pair[1]] = int(pair[0])

        #print (f"main='{main}', inner='{inner}', contains='{contains}'")

        self.add_bag(main, contains)

    def read_file(self, filename):
        with open(filename, "r") as f:
            for line in f:
                self.parse_bag(line)

    def total_contained(self, colour):
        """
        For a bag 'colour', return the total number of bags that can contain it.
        """

        target = self._bags.get(colour)
        if target is None:
            return 0

        ret = target.contained
        queue = Queue()
        [queue.put(bag) for bag in ret]

        while queue.empty() is not True:
            # Getting an item removes it from the queue
            current = self._bags.get(queue.get())
            if current is None:
                continue
            for bag in current.contained:
                if bag not in ret:
                    ret.append(bag)
                    queue.put(bag)

        #print (f"Containing: {ret}")
        return len(ret)

    def total_contains(self, colour):
        """Given a bag 'colour', return the number of bags it must contain."""

        target = self._bags.get(colour)
        if target is None:
            return 0

        total = 0
        for bag, num in target.contains.items():
            total += num + (num * self.total_contains(bag))

        return total

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

    #print (main_baglist)
    target = "shiny gold"
    total_part1  = main_baglist.total_contained(target)
    print (
        f"There are {total_part1} bags that can contain {target} bags."
    )

    total_part2 = main_baglist.total_contains(target)
    print (
        f"{target} bags are required to contain {total_part2} bags."
    )
