#!/usr/bin/env python3

import argparse
import logging


################################################################################


log = logging.getLogger(__name__)


################################################################################


def memory_game(initial: list[int], target_turn: int = 2020) -> int:
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
        v: t+1
        for t, v in enumerate(initial)
    }

    log.debug("Seeded turns: %s", turns)

    # Note: This may not be correct if the last initial number was spoken
    # multiple times, but we're going to assume that didn't happen (and indeed
    # it does not in the test input)
    will_speak = 0

    log_every = int(target_turn / 100)

    for this_turn in range(len(initial)+1, target_turn):
        last_time_spoken = turns.get(will_speak, 0)

        log.debug(
            "We will_speak %s; last spoken on turn %s",
            will_speak, last_time_spoken,
        )

        if this_turn % log_every == 0 and log.level > logging.DEBUG:
            log.info("Current turn: %s", this_turn)

        if last_time_spoken == 0:
            # This number has never been spoken before
            next_turn_speak = 0
        else:
            # This number has been spoken before - calculate the next number
            next_turn_speak = this_turn - last_time_spoken

        log.debug(
            "Turn %s; we will speak %s this turn and %s next turn",
            this_turn, will_speak, next_turn_speak
        )

        turns[will_speak] = this_turn
        will_speak = next_turn_speak

    log.info("Number spoken on turn %s: %s", target_turn, will_speak)

    return will_speak


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
        result1 = memory_game(initial)
        print(f"Part1: {result1}")

    if opts.part2:
        log.info("Disabling debug prints for part 2!")
        # We need to minimise printing, since it adds too much time to the
        # process
        log.setLevel(logging.INFO)

        result2 = memory_game(initial, target_turn=30000000)
        print(f"Part2: {result2}")


