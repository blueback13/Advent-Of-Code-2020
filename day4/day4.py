#!/usr/bin/env python3

import argparse
import copy
import math

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

    def is_valid_v2(self):
        """
        Return true only if all values are within the valid range.

        birth_year - between 1920 and 2002 (inclusive)
        issue_year - between 2010 and 2020 (inclusive)
        expiration_year - between 2020 and 2030 (inclusive)
        height - A number (H) followed by either 'cm' or 'in'
                 If cm then H must be between 150 and 193 (inclusive)
                 If in then H must be between 59 and 76 (inclusive)
        hair_colour - A '#' followed by six characters (0-9, a-f are acceptable)
        eye_colour - One of 'amb', 'blu', 'brn', 'gry', 'grn', 'hzl', 'oth'.
        passport_id - A 9-digit number (leading zeros are counted)
        """

        # Check for missing fields (other than country_id).
        if not self.is_valid():
            return False

        # Height
        if self.height.endswith("cm"):
            height = (150 <= int(self.height[:-2]) <= 193)
        elif self.height.endswith("in"):
            height = (59 <= int(self.height[:-2]) <= 76)
        else:
            height = False
        # DOB
        birth = (1920 <= int(self.birth_year) <= 2002)
        # issue year
        issue = (2010 <= int(self.issue_year) <= 2020)
        # expiration year
        expire = (2020 <= int(self.expiration_year) <= 2030)
        # Hair Color
        allowed = set('0123456789abcdef')
        hair = ((self.hair_colour[0] == '#') and
                (set(self.hair_colour[1:]).issubset(allowed)))
        # Eye Color
        eye = (self.eye_colour in
               ["amb", "blu", "brn", "gry", "grn", "hzl", "oth"]
        )
        # Passport ID
        passport = (len(self.passport_id) == 9 and self.passport_id.isdigit())

        #print(f"is_valid_v2(): height = {height}, birth = {birth}, "
        #      + f"issue = {issue}, hair = {hair}, eye = {eye}, "
        #      + f"passport = {passport}")

        return not False in {birth, issue, expire, height, hair, eye, passport}

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
        #else:
        #    print ("Not valid? {}".format(passport))

    return count


################################################################################


def count_valid_v2(passports):
    """Count the number of passports that are valid, version 2."""
    count = 0
    for passport in passports:
        #print ("checking {}".format(passport))
        if passport.is_valid_v2():
            count += 1
        #else:
        #    print ("Not valid? {}".format(passport))

    return count


################################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find the number of trees that will be hit."
    )

    parser.add_argument("filename")

    opts = parser.parse_args()

    passports = read_passports(opts.filename)

    print("V1: There are {} valid passports.".format(count_valid(passports)))

    print("V2: There are {} valid passports.".format(count_valid_v2(passports)))
