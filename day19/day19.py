#!/usr/bin/env python3

import argparse
import collections
import logging
import re

################################################################################


log = logging.getLogger(__name__)


################################################################################


class Pattern():
    """A pattern"""
    def __init__(
        self,
        index: int,
        references: list[tuple[int]] = None,
        pattern: str = None,
    ) -> None:
        self._index = index
        self._references = references
        self._pattern = pattern

        if self._references is None and self._pattern is None:
            raise RuntimeError(
                "Patterns with neither a pattern nor any references are"
                " unsupported",
                references, pattern,
            )

    @classmethod
    def from_str(cls, string: str):
        """
        Create a Pattern from an input string

        Input strings should take the form:
          3: 4 5 | 5 4
        OR
          4: "a"
        """

        index, data = string.split(":")

        index = int(index)
        data = data.strip()

        if data.startswith('"') and data.endswith('"'):
            return cls(index, pattern=data.strip('"'))

        references = [
            tuple(int(x) for x in subpattern.strip().split())
            for subpattern in data.split("|")
        ]
        return cls(index, references=references)

    @property
    def index(self) -> int:
        return self._index

    @property
    def references(self) -> list[tuple[int]]:
        return self._references

    @property
    def pattern(self) -> str:
        return self._pattern

    @pattern.setter
    def pattern(self, value: str) -> None:
        self._pattern = value

    def valid(self) -> bool:
        """
        Return True if this pattern is valid

        Patterns are valid if they have either (or both of):
          A list of references to other patterns
          A pre-resolved pattern
        """
        return (
            self.references is not None
            or self.pattern is not None
        )

    def __repr__(self) -> str:
        return (
            f"Pattern(index={self._index}, references={self.references},"
            f" pattern={self.pattern!r})"
        )

    def __str__(self) -> str:
        return str(
            self.pattern if self.pattern is not None else self.references
        )


################################################################################


def compile_regex(definitions: dict[int, Pattern], index: int) -> re.Pattern:
    """Resolve the definition at 'index' into a regex pattern"""
    # Queue of definitions to resolve
    queue = collections.deque()
    queue.append(definitions[index])

    while len(queue) > 0:
        resolving = queue.pop()
        if not resolving.valid():
            raise RuntimeError(
                "Cannot resolve regex: Pattern has no pattern, nor any"
                " references",
                pattern,
            )
        elif resolving.pattern is not None:
            # We don't need to regenerate this pattern
            continue

        # Set of all indexes that we need patterns for to calculate the current
        # pattern
        needed = {x for t in resolving.references for x in t}
        if not all([definitions[i].pattern is not None for i in needed]):
            # Re-add the current pattern to the queue
            queue.append(resolving)
            # Add all needed but unknown indexes to the queue
            for i in needed:
                queue.append(definitions[i])
            continue

        # All needed indexes are already resolved
        # We can now generate the regex string for the current pattern
        sub_patterns = [
            "|".join([f"({definitions[i].pattern})" for i in TUPLE])
            for TUPLE in resolving.references
        ]

        pattern = "|".join(
            f"({p})" for p in sub_patterns
        )

        resolving.pattern = pattern

    # Remember to match the start and end of a string in the output pattern
    return re.compile(f"^{definitions[index].pattern}$")


################################################################################


def read_input(in_file: str) -> tuple[list[Pattern], list[str]]:
    """Read and input file and return a list of patterns and strings"""
    with open(in_file) as fh:
        patterns = []
        while True:
            line = fh.readline().strip()
            if line == "":
                # Reached the blank line - next comes the strings to match
                break

            patterns.append(Pattern.from_str(line))

        strings = [l.strip() for l in fh]

    return ({p.index: p for p in patterns}, strings)

################################################################################


if __name__ == "__main__":
    logging.basicConfig()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(
        description="Math homework processor"
    )

    parser.add_argument("input_file")
    parser.add_argument("--part1", action=argparse.BooleanOptionalAction)
    parser.add_argument("--part2", action=argparse.BooleanOptionalAction)

    opts = parser.parse_args()

    patterns, strings = read_input(opts.input_file)

    for p in patterns:
        print(str(p))
    print("\n")
    for s in strings:
        print(s)

    if opts.part1:
        regex = compile_regex(patterns, 0)
        print(f"  regex={regex}")
        result1 = "TODO"
        print(f"Part1: {result1}")

    if opts.part2:
        result2 = 0
        "TODO"
        print(f"Part2: {result2}")
