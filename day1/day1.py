#!/usr/bin/env python3

import argparse

################################################################################

def get_result_2(numbers, target=2020):
    """
    Find the two values in 'numbers' that sum to 2020 and return the result of
    multiplying them together.
    """
    numbers.sort()
    # The numbers are sorted in ascending order, so the smallest numbers are
    # pointed to by i, and the largest numbers are pointed to by j.
    small = 0
    large = len(numbers) - 1
    while small < large:
        num1 = numbers[small]
        num2 = numbers[large]
        sum1 = num1 + num2
        if sum1 == target:
            # This is the target numbers
            return (num1, num2, num1 * num2)
        elif sum1 < target:
            # This means that the smaller number is not yet big enough.
            small += 1
        elif sum1 > target:
            # This means that the larger number is now too big.
            large -= 1


################################################################################

def get_result_3(numbers, target=2020):
    """
    Find the three values in 'numbers' that sum to 2020 and return the result of
    multiplying them together.

    This algorithm sucks lol.
    """
    numbers.sort()
    # The numbers are sorted in ascending order, so the smallest numbers are
    # pointed to by i, and the largest numbers are pointed to by j.
    small = 0
    middle = small + 1
    large = len(numbers) - 1
    while small < large:
        num1 = numbers[small]
        num2 = numbers[middle]
        num3 = numbers[large]
        sum1 = num1 + num2 + num3
        if sum1 == target:
            # This is the target numbers
            return (num1, num2, num3, num1 * num2 * num3)
        elif sum1 < target:
            # This means that the smaller number is not yet big enough.
            if middle < large - 1:
                middle += 1
            else:
                small += 1
                middle = small + 1
        elif sum1 > target:
            # This means that the larger number is now too big.
            large -= 1
            small = 0
            middle = small + 1

################################################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Find the numbers and return the multiple."
    )

    parser.add_argument('filename')

    opts = parser.parse_args()

    numbers = []

    with open(opts.filename, 'r') as f:
        for line in f:
            numbers.append(int(line))


    num1, num2, result = get_result_2(numbers)

    print ("The multiplied value is: {}".format(result))
    print ("The source numbers are: {} + {} = {}".format(num1, num2, num1+num2))


    num1, num2, num3, result2 = get_result_3(numbers)

    print ("\nThe multiplied value is: {}".format(result2))
    print ("The source numbers are: {} + {} + {} = {}".format(num1, num2, num3, num1+num2+num3))
