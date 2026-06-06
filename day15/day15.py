#!/usr/bin/env python3

import argparse
import logging


################################################################################


log = logging.getLogger(__name__)


################################################################################


def part1(initial: list[int], target_turn: int = 2020) -> int:
    """Return the number spoken on turn number 'target_turn'"""
    if not initial or len(initial) < 1:
        raise ValueError("No initial numbers were passed!", initial)

    log.info(
        "Finding number spoken on turn %s for input %s", target_turn, initial,
    )

    # Format: dict[int, list[int]]
    # Where
    #  - The key is the number
    #  - The value is a list of all turns the number was spoken on
    turns = {
        # Seed the dict with the initial numbers
        v: [ t+1 ]
        for t, v in enumerate(initial)
    }

    log.debug("Seeded turns: %s", turns)

    # Number spoken on the last turn
    just_spoke = initial[-1]
    for this_turn in range(len(initial)+1, target_turn+1):
        just_spoke_turns = turns.get(just_spoke, [])

        log.debug(
            "We just_spoke %s; it has been spoken %s times",
            just_spoke, len(just_spoke_turns),
        )

        if 0 <= len(just_spoke_turns) <= 1:
            # This number has never been spoken before, or has only been spoken
            # once before
            will_speak = 0
        else:
            most_recent = just_spoke_turns[-1]
            second_most_recent = just_spoke_turns[-2]
            will_speak = most_recent - second_most_recent

        log.info("Turn %s; we will speak %s", this_turn, will_speak)

        will_speak_turns = turns.get(will_speak, [])
        will_speak_turns.append(this_turn)
        turns[will_speak] = will_speak_turns
        just_spoke = will_speak

    log.info("Number spoken on turn %s: %s", target_turn, just_spoke)

    return just_spoke


################################################################################


def read_input(in_file: str) -> list[int]:
    """Read the input file and return the starting numbers as a list"""
    with open(in_file) as fh:
        line = fh.readline().strip()

    ret = [int(x) for x in line.split(",")]

    return ret


################################################################################


if __name__ == "__main__":
    logging.basicConfig()
    log.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser(
        description="Bus timetable reader"
    )

    parser.add_argument("input_file")
    parser.add_argument("--part1", action=argparse.BooleanOptionalAction)
    parser.add_argument("--part2", action=argparse.BooleanOptionalAction)

    opts = parser.parse_args()

    initial = read_input(opts.input_file)

    if opts.part1:
        result1 = part1(initial)
        print(f"Part1: {result1}")

    if opts.part2:
        result2 = "TODO"
        print(f"Part2: {result2}")


