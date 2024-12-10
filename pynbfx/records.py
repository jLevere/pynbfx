from .parser import Parser
from .result import Result

import struct

from xml.etree.ElementTree import Element

from io import BytesIO

import decimal

import datetime
import base64

from .dictonary import DICTIONARY

from .utils import letter_in_range

from .combinators import (
    success,
    sequence,
    type_selector,
    byte_parser,
    byte_peak,
    signed_int_x_parser,
    static_str,
    int31_parser,
    dict_parser,
    many,
    many_while_prefix,
    string_parser,
    failure,
)


"""
Text parsers
"""


def zero_text_parser() -> Parser:
    """ZeroText Record 0x80"""
    return success("0")


def one_text_parser() -> Parser:
    """OneText Record 0x82"""
    return success("1")


def false_text_parser() -> Parser:
    """FalseText Record 0x84"""
    return success("false")


def true_text_parser() -> Parser:
    """TrueText Record 0x86"""
    return success("true")


def int8_text_parser() -> Parser:
    """Int8Text Record 0x88"""
    return signed_int_x_parser(1)


def int16_text_parser() -> Parser:
    """Int16Text Record 0x8A"""
    return signed_int_x_parser(2)


def int32_text_parser() -> Parser:
    """Int32Text Record 0x8C"""
    return signed_int_x_parser(4)


def int64_text_parser() -> Parser:
    """Int64Text Record 0x8E"""
    return signed_int_x_parser(8)


def float_text_parser() -> Parser:
    """FloatText Record 0x90"""

    def float_text_fn(stream: BytesIO) -> Result:
        if not (result := byte_parser(4)(stream)):
            return result
        float_value = struct.unpack("f", result.unwrap())[0]

        if float_value == float("inf"):
            return Result.ok(stream, "INF")
        elif float_value == float("-inf"):
            return Result.ok(stream, "-INF")
        elif float_value != float_value:
            return Result.ok(stream, "NaN")
        elif float_value == 0.0 and (1.0 / float_value) < 0:
            return Result.ok(stream, "-0")

        formatted_value = f"{float_value:.10g}"

        return Result.ok(stream, formatted_value)

    return Parser(float_text_fn)


def double_text_parser() -> Parser:
    """DoubleText Record 0x92"""

    def double_text_fn(stream: BytesIO) -> Result:
        if not (result := byte_parser(8)(stream)):
            return result

        double_value = struct.unpack("d", result.unwrap())[0]

        if double_value == float("inf"):
            return Result.ok(stream, "INF")
        elif double_value == float("-inf"):
            return Result.ok(stream, "-INF")
        elif double_value != double_value:
            return Result.ok(stream, "NaN")
        elif double_value == 0.0 and (1.0 / double_value) < 0:
            return Result.ok(stream, "-0")

        formatted_value = f"{double_value:.10g}"

        return Result.ok(stream, formatted_value)

    return Parser(double_text_fn)


def decimal_text_parser() -> Parser:
    """DecimalText Record 0x94"""

    def decimal_text_fn(stream: BytesIO) -> Result:
        if not (result := byte_parser(16)(stream)):
            return result

        dec = decimal.Decimal(int.from_bytes(result.unwrap()))

        if dec.is_infinite():
            return Result.ok(stream, "INF" if dec > 0 else "-INF")
        elif dec.is_nan():
            return Result.ok(stream, "NaN")
        elif dec.is_zero():
            return Result.ok(stream, "0")

        decimal_str = str(dec).rstrip("0").rstrip(".")
        return Result.ok(stream, decimal_str)

    return Parser(decimal_text_fn)


def datetime_text_parser() -> Parser:
    """DatetimeText Record 0x96"""

    def datetime_text_fn(stream: BytesIO) -> Result:
        if not (result := byte_parser(8)(stream)):
            return result
        value = int.from_bytes(result.unwrap())

        tz = value & 0b11
        # Extract the 62-bit datetime value
        total_100ns = value >> 2

        base_date = datetime.datetime(1, 1, 1)
        delta = datetime.timedelta(
            microseconds=total_100ns / 10
        )  # Convert to microseconds
        dt = base_date + delta

        if tz == 1:
            return Result.ok(stream, dt.isoformat() + "Z")
        elif tz == 2:
            # TODO: see MC-NBFX: 2.2.3.1.2
            # This needs to set an offset feild from UTC to local time
            return Result.ok(stream, dt.isoformat())

        return Result.ok(stream, dt.isoformat())

    return Parser(datetime_text_fn)


def chars8_text_parser() -> Parser:
    """Chars8Text Record 0x98"""

    return (
        byte_parser()
        .bind_ignore(lambda length: byte_parser(length))
        .bind_ignore(lambda s: success(s.decode("utf-8")))
    )


def chars16_text_parser() -> Parser:
    """Chars16Text Record 0x9A"""

    return (
        byte_parser()
        .bind_ignore(lambda length: byte_parser(length))
        .bind_ignore(lambda s: success(s.decode("utf-8")))
    )


def chars32_text_parser() -> Parser:
    """Chars32Text Record 0x9C"""

    return (
        byte_parser()
        .bind_ignore(lambda length: byte_parser(length))
        .bind_ignore(lambda s: success(s.decode("utf-8")))
    )


def bytes8_text_parser() -> Parser:
    """Bytes8Text Record 0x9E"""

    return (
        byte_parser()
        .bind_ignore(lambda length: byte_parser(length))
        .bind_ignore(lambda bs: success(bs))
        .map(lambda s: base64.b64encode(s).decode("utf-8"))
    )


def bytes16_text_parser() -> Parser:
    """Bytes16Text Record 0xA0"""

    return (
        byte_parser()
        .bind_ignore(lambda length: byte_parser(length))
        .bind_ignore(lambda bs: success(bs))
        .map(lambda s: base64.b64encode(s).decode("utf-8"))
    )


def bytes32_text_parser() -> Parser:
    """Bytes32Text Record 0xA2"""

    return (
        byte_parser()
        .bind_ignore(lambda length: byte_parser(length))
        .bind_ignore(lambda bs: success(bs))
        .map(lambda s: base64.b64encode(s).decode("utf-8"))
    )


def start_list_text_parser() -> Parser:
    """StartListText Record 0xA4"""

    return success("")


def end_list_text_parser() -> Parser:
    """EndListText Record 0xA6"""

    return success("")


def empty_text_parser() -> Parser:
    """EmptyText Record 0xA8"""

    return success("")


def dictionary_text_parser() -> Parser:
    """DictionaryText Record 0xAA"""

    return dict_parser(DICTIONARY)


def unique_id_text_parser() -> Parser:
    """UniqueIdText Record 0xAC"""

    return sequence(
        byte_parser(4),
        byte_parser(2),
        byte_parser(2),
        byte_parser(2),
        byte_parser(6),
    ).map(
        lambda r: f"urn:uuid:{r[0].hex()}-{r[1].hex()}-{r[2].hex()}-{r[3].hex()}-{''.join(r[4][i:i+2].hex() for i in range(0, 8, 2))}"
    )


def time_span_text_parser() -> Parser:
    """TimeSpanText Record 0xAE"""

    def time_span_text_fn(stream: BytesIO) -> Result:
        if not (result := byte_parser(8)(stream)):
            return result

        # Interpret the 8-byte value as a signed integer
        value = int.from_bytes(result.unwrap(), byteorder="little", signed=True)

        # Convert to the appropriate format based on conditions
        days, remainder = divmod(value, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        if days != 0 and seconds == 0:
            return Result.ok(stream, f"{days}.{hours:02}:{minutes:02}:{seconds:02}")
        elif days != 0:
            return Result.ok(stream, f"{days}.{hours:02}:{minutes:02}:{seconds:02}")
        elif seconds == 0:
            return Result.ok(stream, f"{hours:02}:{minutes:02}:{seconds:02}")
        else:
            return Result.ok(stream, f"{hours:02}:{minutes:02}:{seconds:02}")

    return Parser(time_span_text_fn)


def uuid_text_parser() -> Parser:
    """UuidText Record 0xB0"""

    return sequence(
        byte_parser(4),
        byte_parser(2),
        byte_parser(2),
        byte_parser(2),
        byte_parser(6),
    ).map(
        lambda result: f"{result[0].hex()}-{result[1].hex()}-{result[2].hex()}-{result[3].hex()}-{''.join(result[4][i:i+2].hex() for i in range(0, 8, 2))}"
    )


def uint64_text_parser() -> Parser:
    """UInt64Text Record 0xB2"""

    def uint64_text_fn(stream: BytesIO) -> Result:
        if not (result := byte_parser(8)(stream)):
            return result

        # Interpret the 8-byte value as an unsigned integer
        value = int.from_bytes(result.unwrap(), byteorder="little", signed=False)

        # Return the string representation of the unsigned integer
        return Result.ok(stream, str(value))

    return Parser(uint64_text_fn)


def bool_text_parser() -> Parser:
    """BoolText Record 0xB4"""
    return byte_parser(1).map(lambda b: "true" if b else "false")


def unicode_chars8_text_parser() -> Parser:
    """UnicodeChars8Text Record 0xB6"""

    return (
        byte_parser()
        .bind_ignore(lambda length: byte_parser(length))
        .map(lambda utf16_bytes: utf16_bytes.decode("utf-16"))
    )


def unicode_chars16_text_parser() -> Parser:
    """UnicodeChars16Text Record 0xB8"""

    return (
        byte_parser(2)
        .bind_ignore(lambda length: byte_parser(int.from_bytes(length)))
        .map(lambda utf16_bytes: utf16_bytes.decode("utf-16"))
    )


def unicode_chars32_text_parser() -> Parser:
    """UnicodeChars32Text Record 0xBA"""

    return (
        int31_parser()
        .bind_ignore(lambda length: byte_parser(length))
        .map(lambda utf16_bytes: utf16_bytes.decode("utf-16"))
    )


def qname_dictionary_text_parser() -> Parser:
    """QNameDictionaryText Record 0xBC"""

    return byte_parser().bind_ignore(
        lambda prefix: dict_parser(DICTIONARY).bind_ignore(
            lambda name: success(f"{chr(ord('a') + prefix)}:{name}")
        )
    )


"""
Primary type parsers
"""

END_TAG = 0x01


ATTRIBUTE_TYPES = range(0x04, 0x3F)

SHORT_ATTRIBUTE = 0x04
ATTRIBUTE = 0x05
SHORT_DICTIONARY_ATTRIBUTE = 0x06
DICTIONARY_ATTRIBUTE = 0x07
SHORT_XMLNS_ATTRIBUTE = 0x08
XMLNS_ATTRIBUTE = 0x09
SHORT_DICTIONARY_XMLNS_ATTRIBUTE = 0x0A
DICTIONARY_XMLNS_ATTRIBUTE = 0x0B

PREFIX_ATTRIBUTES = range(0x26, 0x3F)
PREFIX_DICTIONARY_ATTRIBUTES = range(0x0C, 0x25)


GROUP_ATTRIBUTES_WITH_PREFIX = (
    list(PREFIX_ATTRIBUTES)
    + list(PREFIX_DICTIONARY_ATTRIBUTES)
    + [ATTRIBUTE, DICTIONARY_ATTRIBUTE]
)
GROUP_DICTIONARY_ATTRIBUTES = list(PREFIX_DICTIONARY_ATTRIBUTES) + [
    DICTIONARY_ATTRIBUTE,
    SHORT_DICTIONARY_ATTRIBUTE,
]


ELEMENT_TYPES = range(0x40, 0x77)

SHORT_ELEMENT = 0x40
ELEMENT = 0x41
SHORT_DICTIONARY_ELEMENT = 0x42
DICTIONARY_ELEMENT = 0x43

PREFIX_DICTIONARY_ELEMENTS = range(0x44, 0x5D)
PREFIX_ELEMENTS = range(0x5E, 0x77)


TEXT_TYPES = range(0x80, 0xBD)


GROUP_ELEMENTS_WITH_PREFIX = (
    list(PREFIX_ELEMENTS)
    + list(PREFIX_DICTIONARY_ELEMENTS)
    + [ELEMENT, DICTIONARY_ELEMENT]
)
GROUP_DICTIONARY_ELEMENTS = list(PREFIX_DICTIONARY_ELEMENTS) + [
    DICTIONARY_ELEMENT,
    SHORT_DICTIONARY_ELEMENT,
]


def text_parser() -> Parser:
    return type_selector(
        {
            0x80: zero_text_parser(),
            0x81: zero_text_parser(),
            0x82: one_text_parser(),
            0x83: one_text_parser(),
            0x84: false_text_parser(),
            0x85: false_text_parser(),
            0x86: true_text_parser(),
            0x87: true_text_parser(),
            0x88: int8_text_parser(),
            0x89: int8_text_parser(),
            0x8A: int16_text_parser(),
            0x8B: int16_text_parser(),
            0x8C: int32_text_parser(),
            0x8D: int32_text_parser(),
            0x8E: int64_text_parser(),
            0x8F: int64_text_parser(),
            0x90: float_text_parser(),
            0x91: float_text_parser(),
            0x92: double_text_parser(),
            0x93: double_text_parser(),
            0x94: decimal_text_parser(),
            0x95: decimal_text_parser(),
            0x96: datetime_text_parser(),
            0x97: datetime_text_parser(),
            0x98: chars8_text_parser(),
            0x99: chars8_text_parser(),
            0x9A: chars16_text_parser(),
            0x9B: chars16_text_parser(),
            0x9C: chars32_text_parser(),
            0x9D: chars32_text_parser(),
            0x9E: bytes8_text_parser(),
            0x9F: bytes8_text_parser(),
            0xA0: bytes16_text_parser(),
            0xA1: bytes16_text_parser(),
            0xA2: bytes32_text_parser(),
            0xA3: bytes32_text_parser(),
            0xA4: start_list_text_parser(),
            0xA5: start_list_text_parser(),
            0xA6: end_list_text_parser(),
            0xA7: end_list_text_parser(),
            0xA8: empty_text_parser(),
            0xA9: empty_text_parser(),
            0xAA: dictionary_text_parser(),
            0xAB: dictionary_text_parser(),
            0xAC: unique_id_text_parser(),
            0xAD: unique_id_text_parser(),
            0xAE: time_span_text_parser(),
            0xAF: time_span_text_parser(),
            0xB0: uuid_text_parser(),
            0xB1: uuid_text_parser(),
            0xB2: uint64_text_parser(),
            0xB3: uint64_text_parser(),
            0xB4: bool_text_parser(),
            0xB5: bool_text_parser(),
            0xB6: unicode_chars8_text_parser(),
            0xB7: unicode_chars8_text_parser(),
            0xB8: unicode_chars16_text_parser(),
            0xB9: unicode_chars16_text_parser(),
            0xBA: unicode_chars32_text_parser(),
            0xBB: unicode_chars32_text_parser(),
            0xBC: qname_dictionary_text_parser(),
            0xBD: qname_dictionary_text_parser(),
        }
    )


def tag_prefix_parser(record_type: int) -> Parser:
    """Parses the prefix to a tag.  Works for both elements and attributes

    Args:
        record_type (int): the type of the current record

    Returns:
        Parser: parser which returns the prefix to the tag of the current record
    """

    def tag_prefix_parser_fn(stream: BytesIO) -> Result:
        if record_type in [
            XMLNS_ATTRIBUTE,
            DICTIONARY_XMLNS_ATTRIBUTE,
        ]:
            return Result.ok(stream, "xmlns:")

        if record_type not in GROUP_ATTRIBUTES_WITH_PREFIX + GROUP_ELEMENTS_WITH_PREFIX:
            return Result.ok(stream, "")

        if (
            record_type in PREFIX_DICTIONARY_ATTRIBUTES
            or record_type in PREFIX_DICTIONARY_ELEMENTS
        ):
            return Result.ok(
                stream,
                letter_in_range(
                    record_type,
                    PREFIX_DICTIONARY_ELEMENTS
                    if record_type in PREFIX_DICTIONARY_ELEMENTS
                    else PREFIX_DICTIONARY_ATTRIBUTES,
                )
                + ":",
            )
        if record_type in PREFIX_ELEMENTS or record_type in PREFIX_ATTRIBUTES:
            return Result.ok(
                stream,
                letter_in_range(
                    record_type,
                    PREFIX_ELEMENTS
                    if record_type in PREFIX_ELEMENTS
                    else PREFIX_ATTRIBUTES,
                )
                + ":",
            )
        return string_parser().map(lambda res: res + ":")(stream)

    return Parser(tag_prefix_parser_fn)


def tag_name_parser(record_type: int) -> Parser:
    """Parse tag name value

    Args:
        record_type (int): type of the current record

    Returns:
        Parser: parser which returns the string value of the tag.
    """

    def tag_name_parser_fn(stream: BytesIO) -> Result:
        if record_type in [SHORT_XMLNS_ATTRIBUTE, SHORT_DICTIONARY_XMLNS_ATTRIBUTE]:
            return Result.ok(stream, "xmlns")

        if record_type in GROUP_DICTIONARY_ATTRIBUTES + GROUP_DICTIONARY_ELEMENTS:
            return dict_parser(DICTIONARY)(stream)

        return string_parser()(stream)

    return Parser(tag_name_parser_fn)


def attribute_parser() -> Parser:
    def parse_attribte_fn(stream: BytesIO) -> Result:
        if not (result := byte_parser()(stream)):
            return result
        record_type = result.unwrap()
        if record_type not in ATTRIBUTE_TYPES:
            return Result.err(stream, "Not Attribute Record")

        if not (result := tag_prefix_parser(record_type)(stream)):
            return result
        prefix = result.unwrap()

        if not (result := tag_name_parser(record_type)(stream)):
            return result
        name = result.unwrap()

        # what type of parser for the value
        if record_type in [XMLNS_ATTRIBUTE, SHORT_XMLNS_ATTRIBUTE]:
            result = string_parser()(stream)
        elif record_type in [
            SHORT_DICTIONARY_XMLNS_ATTRIBUTE,
            DICTIONARY_XMLNS_ATTRIBUTE,
        ]:
            result = dict_parser(DICTIONARY)(stream)
        else:
            result = text_parser()(stream)
        if result.is_err():
            return result
        value = result.unwrap()

        return Result.ok(stream, {prefix + name: value})

    return Parser(parse_attribte_fn)


def element_parser() -> Parser:
    def parse_element_fn(stream: BytesIO) -> Result:
        if not (result := byte_parser()(stream)):
            return result
        record_type = result.unwrap()

        if record_type == END_TAG:
            return Result.ok(stream, "End Elem tag")
        # TODO: this end tags should be treated as an error
        # if seen here.  if they are seen farther down, like in attributes
        # or text then should just return root. See [MC-NBFX]: 2.3.1
        # ======= update =======
        # this is even more annoying because its recursive, and legit
        # end tags can be visible here..... It should return an ok, end elem
        # and the aggrogate shouldnt add non elements at the end....

        if record_type not in ELEMENT_TYPES:
            return Result.err(stream, "Not Element Record")

        ########## define parsers ###############
        tag_parser = sequence(
            tag_prefix_parser(record_type), tag_name_parser(record_type)
        ).map(lambda tag: "".join(tag))

        attributes_parser = many_while_prefix(
            attribute_parser(),
            byte_peak(),
            lambda value: value in ATTRIBUTE_TYPES,
        )

        current_element_parser = tag_parser.bind_ignore(
            lambda tag: attributes_parser.bind_ignore(
                lambda attribs: success(
                    Element(tag, **{k: v for d in attribs for k, v in d.items()})
                )
            )
        )
        ########## apply parsers ##################

        if not (result := current_element_parser(stream)):
            return result.aggregate(
                Result.err(stream, f"{current_element_parser.desc()}")
            )
        root: Element = result.unwrap()

        if not (result := byte_peak()(stream)):
            # Getting to end of input is tricky.  It could be mangled input,
            # or it could actually be the end.
            # all we know is that we have a root, so we should assume
            # it is the end and return the root.
            return Result.ok(stream, root)

        peaked_record_type = result.unwrap()

        if peaked_record_type == END_TAG:
            return Result.ok(stream, root)

        if peaked_record_type in TEXT_TYPES:
            if result := text_parser()(stream):
                root.text = result.unwrap()

                if peaked_record_type % 2 == 1:  # is an end record so return root
                    return Result.ok(stream, root)

        childeren_parser = many_while_prefix(
            element_parser(),
            byte_peak(),
            lambda value: value in list(ELEMENT_TYPES),
        )
        if not (result := childeren_parser(stream)):
            return result.aggregate(Result.err(stream, f"{childeren_parser.desc()}"))

        for i in result.unwrap():
            if isinstance(i, Element):
                root.append(i)

        return Result.ok(stream, root)

    return Parser(parse_element_fn)


def record_parser() -> Parser:
    def parse_record_fn(stream: BytesIO) -> Result:
        # Parse the root element and its children
        return element_parser()(stream)

    return Parser(parse_record_fn)
