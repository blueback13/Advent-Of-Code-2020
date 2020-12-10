#!/usr/bin/env python3

import argparse
import copy

################################################################################


class passport:
    """
    This class contains the data for a passport.

    Unset fields are set to a value of None.
    """

    def __init__(
        self,
        byr=None,
        iyr=None,
        eyr=None,
        hgt=None,
        hcl=None,
        ecl=None,
        pid=None,
        cid=None,
    ):
        self.birth_year = byr
        self.issue_year = iyr
        self.expiration_year = eyr
        self.height = hgt
        self.hair_colour = hcl
        self.eye_colour = ecl
        self.passport_id = pid
        self.country_id = cid

    def is_valid(self):
        """Return false if any value other than country_id (cid) is None."""
        return not None in {
            self.birth_year,
            self.issue_year,
            self.expiration_year,
            self.height,
            self.hair_colour,
            self.eye_colour,
            self.passport_id,
            # self.country_id,
        }

    def parse_pair(self, pair):
        """Read a key:value pair into the current state."""
        split = pair.split(":")
        if split[0].lower() == "byr":
            self.birth_year = split[1]
        elif split[0].lower() == "iyr":
            self.issue_year = split[1]
        elif split[0].lower() == "eyr":
            self.expiration_year = split[1]
        elif split[0].lower() == "hgt":
            self.height = split[1]
        elif split[0].lower() == "hcl":
            self.hair_colour = split[1]
        elif split[0].lower() == "ecl":
            self.eye_colour = split[1]
        elif split[0].lower() == "pid":
            self.passport_id = split[1]
        elif split[0].lower() == "cid":
            self.country_id = split[1]

    def __repr__(self):
        return (
            "passport{{birth_year='{}', issue_year='{}', expiration_year='{}', "
            "height='{}', hair_colour='{}', eye_colour='{}', passport_id='{}', "
            "country_id='{}'}}"
        ).format(
            self.birth_year,
            self.issue_year,
            self.expiration_year,
            self.height,
            self.hair_colour,
            self.eye_colour,
            self.passport_id,
            self.country_id,
        )


################################################################################


def read_passports(filename):
    """
    Read a file containing passport information into a list of passports.

    Each passport is defined by key:value pairs. Each pair is seperated by
    either a space or a newline.

    Each passport is separated by a blank line.
    """
    ret = []

    with open(filename, "r") as passports_file:
        current_passport = None
        for line in passports_file:
            if line in {"", "\n"}:
                if current_passport is not None:
                    ret.append(current_passport)
                    current_passport = None
                    continue

            if current_passport is None:
                current_passport = passport()

            pairs = line.split()
            for pair in pairs:
                current_passport.parse_pair(pair)

        if current_passport is not None:
            ret.append(current_passport)

    return ret


################################################################################


def count_valid(passports):
    """Count the number of passports that are valid."""
    count = 0
    for passport in passports:
        if passport.is_valid():
            count += 1
        else:
            print ("Not valid? {}".format(passport))

    return count


################################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find the number of trees that will be hit."
    )

    parser.add_argument("filename")

    opts = parser.parse_args()

    passports = read_passports(opts.filename)

    print("There are {} valid passports.".format(count_valid(passports)))
