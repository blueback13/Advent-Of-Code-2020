#!/usr/bin/env python3

import argparse
import collections
import logging


################################################################################


log = logging.getLogger(__name__)


################################################################################


class Operator():
    """
    Base Operator

    Does nothing itself. Is only used to initialise other operators
    """
    # List of available subclass instances
    _registry = []

    @classmethod
    def _match_op(cls, operator: str) -> bool:
        """Return True if this subclass works on 'operator'"""
        return operator == cls._operator

    def __init_subclass__(cls, **kwargs) -> None:
        """
        Initialise a new command type
        """
        super().__init_subclass__(**kwargs)
        # Note: Operations have no data, so we can treat them as singletons
        cls._registry.append(super().__new__(cls))

    def __new__(cls, operator: str, *args, **kwargs):
        """Return an object of the appropriate subclass for input SeatState"""
        for op in cls._registry:
            if op._match_op(operator):
                return op

        if not newcls:
            raise RuntimeError("No handler for operator!", state)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

    def __str__(self) -> str:
        return self._operator

    def __call__(self, x: int, y: int) -> int:
        """Return the result of applying this operation to x and y"""
        raise NotImplementedError("Must override operation in subclass!")


################################################################################


class Addition(Operator):
    _operator = "+"

    def __call__(self, x: int, y: int) -> int:
        return x + y


################################################################################


class Multiplication(Operator):
    _operator = "*"

    def __call__(self, x: int, y: int) -> int:
        return x * y


################################################################################


def tokenise(string: str) -> list[str]:
    """
    Split a string into tokens

    The expected token types are:
      numbers - strings with all digits
      operators - either '+' or '*'
      brackets - either '(' or ')'
    """

    digits = []

    for char in string:
        if char.isdigit():
            # We're still accumulating the last number
            digits.append(char)
            continue

        if len(digits) > 0:
            # We've reached the end of the number being accumulated
            yield "".join(digits)
            digits = []

        # Handle other token types
        if char.isspace():
            continue
        else:
            yield char

    # We've reached the end of the string
    # Make sure any number that was being accumulated is actually returned
    if len(digits) > 0:
        yield "".join(digits)


################################################################################


class Problem():
    """A math homework problem"""
    def __init__(
        self, problems: list["Problem"] | int, operators: list[Operator] = None,
    ) -> None:
        if isinstance(problems, int):
            self._value = True
            self._probs = [problems]
        else:
            self._value = False
            self._probs = problems

        self._ops = operators if operators is not None else []

        if not (
            isinstance(self._probs, (list, tuple))
            and all([isinstance(x, (type(self), int)) for x in self._probs])
         ):
            raise TypeError(
                "'problems' must be a list of Problems",
                self._probs
            )
        elif not (
            isinstance(self._ops, (list, tuple))
            and all([isinstance(x, Operator) for x in self._ops])
        ):
            raise TypeError(
                "'operators' must be a list of Operators", self._ops
            )
        elif not (len(self._probs) == len(self._ops) + 1):
            raise RuntimeError(
                "Number of operators must be 1 less than number of numbers",
                self._probs, self._ops,
            )

    @classmethod
    def from_string(cls, string: str) -> 'Problem':
        """Return a Problem object matching the equation defined by 'string'"""
        subproblems = []
        operators = []
        bracket_storage = []

        for token in tokenise(string):
            if token.isdigit():
                subproblems.append(cls(int(token)))
                continue
            elif token in ["*", "+"]:
                operators.append(Operator(token))
                continue
            elif token == "(":
                # Start a new subproblem
                bracket_storage.append( (subproblems, operators) )
                subproblems = []
                operators = []
                # log.info(
                #     "Started new subproblem - currently %s brackets deep",
                #     len(bracket_storage),
                # )
                # log.debug("Saved subproblems: %s", bracket_storage)
            elif token == ")":
                # End a subproblem
                if len(bracket_storage) < 1:
                    raise RuntimeError(
                        "Attempted to close bracket without opening a bracket",
                        subproblems, operators, bracket_storage,
                    )

                subproblem = cls(subproblems, operators)
                subproblems, operators = bracket_storage.pop()
                subproblems.append(subproblem)
                # log.info(
                #     "Ended subproblem - currently %s brackets deep",
                #     len(bracket_storage),
                # )
                # log.debug("Saved subproblems: %s", bracket_storage)

        # Reached the end of the problem
        if len(bracket_storage) > 0:
            raise RuntimeError(
                "Reached end of problem without closing all brackets!",
                subproblems, operators, bracket_storage
            )

        return cls(subproblems, operators)

    def evaluate(self) -> int:
        """Return result of evaluating the equation defined by this object"""
        if self._value:
            return self._probs[0]

        total = self._probs[0].evaluate()

        for operation, problem in zip(self._ops, self._probs[1:]):
            total = operation(total, problem.evaluate())

        return total

    def evaluate_v2(self) -> int:
        """
        Return result of evaluating the equation defined by this object

        Implements operator precedence as per part 2 of the problem (e.g. '+'
        comes before '*')
        """
        if self._value:
            return self._probs[0]

        # First get the integer values of all subproblems in this problem
        subtotals = [p.evaluate_v2() for p in self._probs]
        operations = [ o for o in self._ops ]

        addition = Operator("+")

        while True:
            try:
                i = operations.index(addition)
            except ValueError:
                # No more additions in the list
                break

            # Run the operation on its target values
            op = operations[i]
            # log.debug(
            #     "Applying operation at %s (%s); subtotals: %s",
            #     i, op, subtotals
            # )

            # Note: We're replacing the first value operated on with the total -
            # the second value operated on will be removed from this list
            subtotals[i] = op(subtotals[i], subtotals[i+1])

            # Remove the operation from the list along with the (now used)
            # second value from the subtotals
            del operations[i]
            del subtotals[i+1]

            # log.debug("Operation complete: %s", subtotals)


        # log.debug(
        #     "Applied all additions (subtotals=%s; operations=%s)",
        #     subtotals, operations,
        # )

        # Apply remaining operations
        total = subtotals[0]
        for operation, subtotal in zip(operations, subtotals[1:]):
            # log.debug(
            #     "Applying operation %s to %s and %s",
            #     operation, total, subtotal,
            # )
            total = operation(total, subtotal)

        return total

    def __len__(self) -> int:
        """Return number of subproblems in this problem"""
        if self._value:
            return 1

        return sum([len(p) for p in self._probs])

    def __str__(self) -> str:
        if not self._value and len(self._probs[0]) > 1:
            ret = f"({self._probs[0]})"
        else:
            ret = str(self._probs[0])

        if len(self._probs) > 1:
            ret += " " + " ".join([
                str(o) + " " + (f"({p})" if len(p) > 1 else str(p))
                for o, p in zip(self._ops, self._probs[1:])
            ])

        return ret


################################################################################


def read_input(in_file: str) -> list[Problem]:
    """Read an input file and return the files from within"""
    ret = []
    with open(in_file) as fh:
        for line in fh:
            ret.append(Problem.from_string(line.strip()))

    return ret


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

    problems = read_input(opts.input_file)

    if opts.part1:
        result1 = 0
        for problem in problems:
            _result = problem.evaluate()
            log.info("Part 1: Problem: %s = %s", problem, _result)
            result1 += _result

        print(f"Part1: {result1}")

    if opts.part2:
        result2 = 0
        for problem in problems:
            _result = problem.evaluate_v2()
            log.info("Part 2: Problem: %s = %s", problem, _result)
            result2 += _result
        print(f"Part2: {result2}")
