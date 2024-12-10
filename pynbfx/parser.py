from io import BytesIO
from typing import Any, Callable, Self

from .result import Result


class Parser:
    def __init__(self, wrapped_fn: Callable[[BytesIO], Result]):
        self.wrapped_fn = wrapped_fn

    def __call__(self, stream: BytesIO) -> Result:
        result = self.wrapped_fn(stream)

        trace_info = f"{self.desc():<20} at position {stream.tell()}"
        if result.is_err():
            trace_info += f" with error: {result.error_msg}"
        else:
            trace_info += f" result: {result.unwrap()}"
        print(trace_info)
        return result

    def desc(self) -> str:
        """Return the name of the current parser

        Returns:
            str: current parser
        """
        return self.wrapped_fn.__name__

    def bind(self, bind_func: Callable[[Any], "Parser"]) -> "Parser":
        """
        Chain dependent parsers together, passing all intermediate results through the chain.

        This method allows you to compose parsers sequentially, where the result of one parser
        is passed to the `bind_func`, which generates a new parser for the next stage of parsing.
        The results from each stage are accumulated and aggregated, so that intermediate values
        are preserved.

        Args:
            bind_func: A function that takes the result of the current parser and returns a new parser
                    based on that result.

        Returns:
            A new `Parser` that applies the chained parsers in sequence, aggregating results.
        """

        def bind_fn(stream: BytesIO) -> Result:
            result = self(stream)
            if result.is_err():
                return result.aggregate(Result.err(stream, f"{self.desc()}"))
            next_parser = bind_func(result)
            return next_parser(stream).aggregate(result)

        return Parser(bind_fn)

    def bind_ignore(self, bind_func: Callable[[Any], "Parser"]) -> "Parser":
        """
        Chain dependent parsers together, discarding all intermediate results.

        This method functions similarly to `bind`, but only the final result from the
        last parser in the chain is kept. Intermediate parsing results are discarded
        once they are no longer needed. This is useful when the focus is solely on
        the final output, and you do not need to accumulate values from earlier stages.

        Args:
            bind_func: A function that takes the result of the current parser and returns a new parser
                    based on that result.

        Returns:
            A new `Parser` that applies the chained parsers in sequence, only preserving the final result.
        """

        def bind_ignore_fn(stream: BytesIO) -> Result:
            result = self(stream)
            if result.is_err():
                return result.aggregate(Result.err(stream, f"{self.desc()}"))
            return bind_func(result.unwrap())(stream)

        return Parser(bind_ignore_fn)

    def map(self, map_function: Callable) -> "Parser":
        """Transforms the output of an initial parser using a mapping function.

        Args:
            map_function (Callable): A function that takes the result of the parser and returns a transformed value.

        Returns:
            Parser: A new parser that applies the mapping function to the result of the initial parser.
        """

        def map_fn(stream: BytesIO) -> Result:
            result = self(stream)
            if result.is_err():
                return result
            return Result.ok(result.stream, map_function(result.unwrap()))

        return Parser(map_fn)

    def times(self, min: int, max: int | None = None) -> "Parser":
        """Creates a parser that expects the initial parser to run between a minimum and maximum number of times.

        If only one argument is given, the parser is expected to run exactly that number of times.

        Args:
            min (int): The minimum number of times the parser should run.
            max (int | None): The maximum number of times the parser can run. Defaults to `min` if None.
        """
        if max is None:
            max = min

        def times_fn(stream: BytesIO) -> Result:
            values = []
            count = 0

            while count < max:
                result = self(stream)
                if result.is_err():
                    break
                values.append(result.unwrap())
                count += 1

            if count < min:
                return Result.err(stream, "Not enough values parsed")

            return Result.ok(stream, values)

        return Parser(times_fn)

    def choice(self, other: Self) -> "Parser":
        """Implements choice between two parsers.

        The parser attempts to apply the first parser. If it succeeds, its value is returned.
        If it fails, the second parser is tried.

        Args:
            other (Self): Another parser to attempt if the first parser fails.

        Returns:
            Parser: A choice parser
        """

        def choice_fn(stream: BytesIO) -> Result:
            init_pos = stream.tell()
            result = self(stream)
            if result.is_ok() or stream.tell() != init_pos:
                return result
            stream.seek(init_pos)
            return other(stream)

        return Parser(choice_fn)
