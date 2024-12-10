
from io import BytesIO

from typing import Callable, Any



from .parser import Parser
from .result import Result






"""
Combinators for a parser combinator
"""


def many(parser: Parser) -> Parser:
    """Parses zero or more instances of the provided parser.

    Repeatedly applies the given parser to the input stream until
    it encounters an error. It collects all successful results into a list and
    returns them as a single result.

    Args:
        parser (Parser): The parser to apply multiple times.

    Returns:
        Parser: A new parser that produces a list of results from zero or more
        applications of the provided parser.
    """

    def many_fn(stream: BytesIO) -> Result:
        results = []
        while True:
            result = parser(stream)
            if result.is_err():
                break
            results.append(result.unwrap())
            stream = result.stream
        return Result.ok(stream, results)

    return Parser(many_fn)


def sequence(*parsers: Parser, **kw_parsers: Parser) -> Parser:
    """
    Executes a series of parsers in order, collecting their results.

    This function allows for running multiple parsers sequentially. Either a list
    of positional parsers or keyword arguments for named parsers can be provided.
    The results are collected into a list for positional parsers or a dictionary
    for keyword parsers.

    Args:
        *parsers (Parser): A variable number of parsers to run in sequence.
        **kw_parsers (Parser): Keyword parsers to run in sequence, with names as keys.

    Returns:
        Parser: A new parser that executes the provided parsers in order and
        returns their results in a list or dictionary.

    Raises:
        ValueError: If both positional and keyword parsers are provided.

    Example:
        >>> result_parser = sequence(byte_parser(), int_parser())
        >>> result = result_parser(stream)

        >>> named_result_parser = sequence(byte_parser=byte_parser(), int_parser=int_parser())
        >>> named_result = named_result_parser(stream)
    """
    if not parsers and not kw_parsers:
        return success([])

    if parsers and kw_parsers:
        raise ValueError("Use either positional arguments or keyword arguments with seq, not both")

    if parsers:

        def seq_fn(stream: BytesIO) -> Result:
            values = []
            for parser in parsers:
                result = parser(stream)
                if result.is_err():
                    return result.aggregate(
                        Result.err(
                            stream,
                            f"current parser {parser.desc()} in sequence  <{','.join([p.desc() for p in parsers])}>",
                        )
                    )
                values.append(result.unwrap())
                stream = result.stream
            return Result.ok(stream, values)

        return Parser(seq_fn)
    else:

        def seq_kwarg_fn(stream: BytesIO):
            values = {}
            for name, parser in kw_parsers.items():
                result = parser(stream)
                if result.is_err():
                    return result.aggregate(
                        Result.err(
                            stream,
                            f"{parser.desc()}, chain: {','.join([p.desc() for p in parsers])}",
                        )
                    )
                values[name] = result.unwrap()
            return Result.ok(stream, values)

        return Parser(seq_kwarg_fn)


def many_while_prefix(
    data_parser: Parser,
    prefix_parser: Parser,
    prefix_check: Callable[[Any], bool],
) -> Parser:
    """Apply and aggrogate results of `data_parser` while the prefix of the stream parsed
    by `prefix_parser` is checked true by prefix_check.

    This can be used to parse a stream of consistant values, each preceeded by a type.

    Args:
        data_parser (Parser): primary parser to collect results from
        prefix_parser (Parser): parses the prefix value
        prefix_check (Callable[[Any], bool]): checks the prefix value

    Returns:
        List of values in Result
    """

    def many_while_prefix_fn(stream: BytesIO) -> Result:
        results = []

        while True:
            prefix = prefix_parser(stream)
            if prefix.is_err() or not prefix_check(prefix.unwrap()):
                break

            result = data_parser(prefix.stream)
            if result.is_err():
                return result.aggregate(Result.err(stream, f"{data_parser.desc()}"))
            results.append(result.unwrap())
            stream = result.stream

        return Result.ok(stream, results)

    return Parser(many_while_prefix_fn)


def test_parse(parser: Parser, test: Callable[[Any], bool]) -> Parser:
    """Parses with parser and tests result value with a function.  If test fails, resets the stream
    back to prepare for another parser.

    Args:
        parser (Parser): parser to use
        test (Callable[[Any], bool]): function to use for check
    """

    def test_parse_fn(stream: BytesIO) -> Result:
        init_pos = stream.tell()
        result = parser(stream)
        if result.is_err():
            return result

        if test(result.unwrap()):
            return result

        stream.seek(init_pos)
        return Result.err(stream, result.unwrap())

    return Parser(test_parse_fn)


def type_selector(type_parsers: dict[int, Parser]) -> Parser:
    """Returns a parser from a list of parsers by type, determined from the first
    byte of the stream.

    Does not consume any from stream if parser is not found.

    Args:
        type_parsers (dict[int, Parser]): type value, parser
    """

    def type_selector_fn(stream: BytesIO) -> Result:
        init_pos = stream.tell()
        prefix = byte_parser()(stream)
        if prefix.is_err():
            return prefix

        type_value = prefix.unwrap()

        sub_parser = type_parsers.get(type_value)
        if not sub_parser:
            stream.seek(init_pos)
            return Result.err(stream, f"Unknown type byte: 0x{type_value:02X}")

        return sub_parser(stream)

    return Parser(type_selector_fn)


def success(value: Any) -> Parser:
    def success_fn(stream: BytesIO) -> Result:
        return Result.ok(stream, value)

    return Parser(success_fn)


def failure(value: Any) -> Parser:
    def failure_fn(stream: BytesIO) -> Result:
        return Result.err(stream, value)

    return Parser(failure_fn)


"""
primatives
"""


def byte_peak() -> Parser:
    """Creates a parser that peeks at the next byte in the stream without consuming it.

    This parser reads one byte from the provided stream but does not advance the
    stream's position, allowing subsequent reads to access the same byte.
    If the stream has reached its end, an error is returned.

    Returns:
        Parser: A parser that allows peeking at the next byte without consuming it.
    """

    def byte_peak_fn(stream: BytesIO) -> Result:
        init_pos = stream.tell()
        byte = stream.read(1)
        if not byte:
            return Result.err(stream, "End of stream")
        stream.seek(init_pos)
        return Result.ok(stream, byte[0])

    return Parser(byte_peak_fn)


def byte_parser(x: int = 1) -> Parser:
    """Creates a parser that reads the next byte from the stream.

    This parser reads one byte from the provided stream and advances the
    stream's position. If the stream has reached its end, an error is returned.

    Args:
        x(int): The number of bytes to read. Defaults to: 1

    Returns:
        Parser: A parser that reads the next byte from the stream.

    Errors:
        - If the stream has reached its end, an error is returned with a message
          indicating "End of stream".
    """

    def byte_parser_fn(stream: BytesIO) -> Result:
        result = stream.read(x)
        if not result or len(result) != x:
            return Result.err(stream, "End of stream")
        return Result.ok(stream, result[0] if x == 1 else result)

    return Parser(byte_parser_fn)


def int31_parser() -> Parser:
    """Creates a parser for a 31-bit unsigned integer using variable-length encoding.

    This parser reads up to five bytes from the provided stream to construct
    a 31-bit unsigned integer. The first four bytes are used for the value,
    while the fifth byte indicates the continuation of the value. The most
    significant bit of each byte is used as a continuation flag. If the flag
    is set to 1, the next byte is part of the integer value; if it is set to 0,
    the parsing stops.

    Returns:
        Parser: A parser that reads from the stream and returns the
                interpreted 31-bit unsigned integer or an error.
    """

    def int31_fn(stream: BytesIO) -> Result:
        maxmbi = 0x7F
        value = 0
        for i in range(5):
            result = byte_parser()(stream)
            if result.is_err():
                return result.aggregate(Result.err(stream, f"{byte_parser().desc()}"))
            v = result.unwrap()
            stream = result.stream
            value |= (v & maxmbi) << 7 * i
            if v & (maxmbi + 1) == 0:
                break
        else:
            return Result.err(stream, "Exceeded max int length")
        return Result.ok(stream, value)

    return Parser(int31_fn)


def signed_int_x_parser(x: int) -> Parser:
    """Creates a parser for a signed integer of a specified byte length.

    This parser reads `x` bytes from the provided stream and interprets
    the bytes as a signed integer using big-endian byte order. If the
    end of the stream is reached before reading `x` bytes, an error
    is returned.

    Args:
        x (int): The number of bytes to read and interpret as a signed integer.
                  This should be between 1 and 8 inclusive to represent
                  the signed integer size (1 byte to 64 bits).

    Returns:
        Parser: A parser that reads `x` bytes from the stream and returns
                the interpreted signed integer or an error.

    Raises:
        ValueError: If `x` is not within the acceptable range (1 to 8).
    """

    if x < 1 or x > 8:
        raise ValueError("x must be between 1 and 8 inclusive.")

    def signed_int_x_fn(stream: BytesIO) -> Result:
        data_bytes = stream.read(x)
        if not data_bytes:
            return Result.err(stream, "End of stream")

        int_val = int.from_bytes(data_bytes, signed=True)
        return Result.ok(stream, int_val)

    return Parser(signed_int_x_fn)


def string_parser() -> Parser:
    """Creates a parser that reads a UTF-8 encoded string from the stream.

    This parser first retrieves the length of the string using the `int31_parser`.
    It then reads that number of bytes from the stream and decodes them into a
    UTF-8 string. If the length of the read string does not match the expected
    length, an error is returned.

    Returns:
        Parser: A parser that reads a UTF-8 encoded string from the stream.

    Example:
        >>> parser = string_parser()
        >>> result = parser(BytesIO(b'\\x05Hello'))
        >>> assert result.unwrap() == "Hello"
    """

    def string_parser_fn(stream: BytesIO) -> Result:
        result = int31_parser()(stream)
        if result.is_err():
            return result.aggregate(Result.err(stream, f"{string_parser().desc()}"))
        length = result.unwrap()
        s = result.stream.read(length)
        if len(s) != length:
            return Result.err(stream, f"Wong sized string, expected {len(s)} got {length}, value: {s}")
        return Result.ok(stream, s.decode("utf-8"))

    return Parser(string_parser_fn)


def dict_parser(dictionary: dict[int, str]) -> Parser:
    """Creates a parser that looks up values in a provided dictionary.

    This parser reads a single byte from the stream and uses its value to
    look up a corresponding string in the provided dictionary. If the
    value is not found in the dictionary, an error is returned.

    Args:
        dictionary (dict[int, str]): A dictionary mapping integer keys to
                                      corresponding string values for lookup.

    Returns:
        Parser: A parser that retrieves the string value associated with
                an integer key from the provided dictionary.

    Example:
        >>> lookup_dict = {0x01: "one", 0x02: "two"}
        >>> stream = BytesIO(b'\\x01')
        >>> parser = dict_parser(lookup_dict)
        >>> result = parser(stream)
        >>> assert result.unwrap() == "one"
    """

    def dict_parser_fn(stream: BytesIO) -> Result:
        result = byte_parser()(stream)
        if result.is_err():
            return result.aggregate(Result.err(stream, f"{dict_parser(dictionary).desc()}"))

        value = result.unwrap()
        s = dictionary.get(value)
        if not s:
            return Result.err(stream, f"Unknown dict lookup value: 0x{value:02X}")
        return Result.ok(stream, s)

    return Parser(dict_parser_fn)


def static_str(s: str) -> Parser:
    """Creates a parser that returns a static string.

    This parser does not read from the stream but instead returns a
    predefined static string value. It is useful for situations where
    a constant string is needed.

    Args:
        s (str): The static string to be returned by the parser.

    Returns:
        Parser: A parser that always returns the provided static string.

    Example:
        >>> parser = static_str("hi fren")
        >>> result = parser(BytesIO())
        >>> assert result.unwrap() == "hi fren"
    """

    def static_str_fn(stream: BytesIO) -> Result:
        return Result.ok(stream, s)

    return Parser(static_str_fn)
