#!/usr/bin/env python3

import argparse
import logging


################################################################################


log = logging.getLogger(__name__)


################################################################################


class XMAS():
    """
    eXchange-Masking Addition System (XMAS) data to be attacked

    Arguments:
      *args  : Raw XMAS data (only used when in_file is not provided)
      in_file: Path to file containing XMAS data
    """

    def __init__(self, *args, in_file=None):
        """Initialise XMAS data from file OR from arguments"""
        self._data = []

        if in_file is not None:
            self.parse_input(in_file)
        else:
            for arg in args:
                self._data.append(int(arg))

    def parse_input(self, in_file) -> None:
        """Parse an input file into XMAS data"""
        if len(self._data) > 0:
            raise RuntimeError("XMAS data already initialised!", in_file, self)

        with open(in_file) as fh:
            for line in fh:
                self._data.append(int(line))

    def __repr__(self):
        return f"XMAS({ ', '.join(str(n) for n in self._data) })"


################################################################################


if __name__ == "__main__":
    logging.basicConfig()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(
        description="Decipher and attack XMAS data"
    )

    parser.add_argument("input_file")

    opts = parser.parse_args()

    data = XMAS(in_file=opts.input_file)

    log.info("Parsed input: %s", data)
