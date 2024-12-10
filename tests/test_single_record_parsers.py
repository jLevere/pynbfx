from io import BytesIO
from unittest import TestCase
from xml.etree import ElementTree as ET

from pynbfx.records import (
    attribute_parser,
    element_parser,
    text_parser,
)


class TestElementParser(TestCase):
    def setUp(self):
        # 0x40
        self.shortElementStream = BytesIO(b"A\x01a\x04test\x01")
        self.shortElementString = "<a:test></a:test>"

        # 0x41
        self.elementStream = BytesIO(b"@\x08Envelope")
        self.elementString = "<Envelope></Envelope>"

        # 0x42
        self.shortDictElementStream = BytesIO(b"B\x02")
        self.shortDictElementString = "<Envelope></Envelope>"

        # 0x43
        self.dictElementStream = BytesIO(b"C\x01x\x02")
        self.dictElementString = "<x:Envelope></x:Envelope>"

        # 0x45
        self.prefixDictElementStream = BytesIO(b"\x45\x02")
        self.prefixDictElementString = "<b:Envelope></b:Envelope>"

        # 0x5E
        self.prefixElementStream = BytesIO(b"\x5e\x08Envelope")
        self.prefixElementString = "<a:Envelope></a:Envelope>"

    def elem_to_str(self, root: ET.Element) -> str:
        return ET.tostring(root, short_empty_elements=False, encoding="unicode")

    def test_zero_depth_no_attrs_short_element(self):
        parser = element_parser()

        result = parser(self.shortElementStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.shortElementString, self.elem_to_str(result.unwrap()))

    def test_zero_depth_no_attrs_element(self):
        result = element_parser()(self.elementStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.elementString, self.elem_to_str(result.unwrap()))

    def test_zero_depth_no_attrs_short_dict_element(self):
        result = element_parser()(self.shortDictElementStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.shortDictElementString, self.elem_to_str(result.unwrap()))

    def test_zero_depth_no_attrs_dict_element(self):
        result = element_parser()(self.dictElementStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.dictElementString, self.elem_to_str(result.unwrap()))

    def test_zero_depth_no_attrs_prefix_dict_element(self):
        result = element_parser()(self.prefixDictElementStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(
            self.prefixDictElementString, self.elem_to_str(result.unwrap())
        )

    def test_zero_depth_no_attrs_prefix_element(self):
        result = element_parser()(self.prefixElementStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.prefixElementString, self.elem_to_str(result.unwrap()))


class TestAttributeParser(TestCase):
    def setUp(self):
        # Each Attribute has the value of a 0x86 record, which is the str "true"

        # 0x04
        self.shortAttributeStream = BytesIO(b"\x04\x04test\x86")
        self.shortAttributeDict = {"test": "true"}

        # 0x05
        self.attributeStream = BytesIO(b"\x05\x01x\x04test\x86")
        self.attributeDict = {"x:test": "true"}

        # 0x06
        self.shortDictionaryAttributeStream = BytesIO(b"\x06\x02\x86")
        self.shortDictionaryAttributeDict = {"Envelope": "true"}

        # 0x07
        self.dictionaryAttributeStream = BytesIO(b"\x07\x01x\x02\x86")
        self.dictionaryAttributeDict = {"x:Envelope": "true"}

        # 0x08
        self.shortXmlnsAttributeStream = BytesIO(b"\x08\x04test")
        self.shortXmlnsAttributeDict = {"xmlns": "test"}

        # 0x09
        self.xmlnsAttributeStream = BytesIO(b"\x09\x01x\x04test")
        self.xmlnsAttributeDict = {"xmlns:x": "test"}

        # 0x0A
        self.shortDictionaryXmlnsAttributeStream = BytesIO(b"\x0a\x02")
        self.shortDictionaryXmlnsAttributeDict = {"xmlns": "Envelope"}

        # 0x0B
        self.dictionaryXmlnsAttributeStream = BytesIO(b"\x0b\x01x\x02")
        self.dictionaryXmlnsAttributeDict = {"xmlns:x": "Envelope"}

        # 0x0C-0x25
        self.prefixDictionaryAttributeStream = BytesIO(b"\x0c\x02\x86")
        self.prefixDictionaryAttributeDict = {"a:Envelope": "true"}

        # 0x26-0x3F
        self.prefixAttributeStream = BytesIO(b"\x26\x01x\x86")
        self.prefixAttributeDict = {"a:x": "true"}

    def test_short_attribute(self):
        result = attribute_parser()(self.shortAttributeStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.shortAttributeDict, result.unwrap())

    def test_attribute(self):
        result = attribute_parser()(self.attributeStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.attributeDict, result.unwrap())

    def test_short_dictionary_attribute(self):
        result = attribute_parser()(self.shortDictionaryAttributeStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.shortDictionaryAttributeDict, result.unwrap())

    def test_dictionary_attribute(self):
        result = attribute_parser()(self.dictionaryAttributeStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.dictionaryAttributeDict, result.unwrap())

    def test_short_xmlns_attribute(self):
        result = attribute_parser()(self.shortXmlnsAttributeStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.shortXmlnsAttributeDict, result.unwrap())

    def test_xmlns_attribute(self):
        result = attribute_parser()(self.xmlnsAttributeStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.xmlnsAttributeDict, result.unwrap())

    def test_short_dictionary_xmlns_attribute(self):
        result = attribute_parser()(self.shortDictionaryXmlnsAttributeStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.shortDictionaryXmlnsAttributeDict, result.unwrap())

    def test_dictionary_xmlns_attribute(self):
        result = attribute_parser()(self.dictionaryXmlnsAttributeStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.dictionaryXmlnsAttributeDict, result.unwrap())

    def test_prefix_dictionary_attribute(self):
        result = attribute_parser()(self.prefixDictionaryAttributeStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.prefixDictionaryAttributeDict, result.unwrap())

    def test_prefix_attribute(self):
        result = attribute_parser()(self.prefixAttributeStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.prefixAttributeDict, result.unwrap())


class TestTextParser(TestCase):
    def setUp(self):
        # ZeroText record (0x80)
        self.zeroTextStream = BytesIO(b"\x80")
        self.zeroTextString = "0"

        # OneText record (0x82)
        self.oneTextStream = BytesIO(b"\x82")
        self.oneTextString = "1"

        # FalseText record (0x84)
        self.falseTextStream = BytesIO(b"\x84")
        self.falseTextString = "false"

        # TrueText record (0x86)
        self.trueTextStream = BytesIO(b"\x86")
        self.trueTextString = "true"

        # Int8Text record (0x88), e.g., -128
        self.int8TextStream = BytesIO(b"\x88\x80")
        self.int8TextString = -128

        # Int16Text record (0x8A), e.g., -32768
        self.int16TextStream = BytesIO(b"\x8a\x80\x00")
        self.int16TextString = -32768

        # Int32Text record (0x8C), e.g., -2147483648
        self.int32TextStream = BytesIO(b"\x8c\x80\x00\x00\x00")
        self.int32TextString = -2147483648

        # Int64Text record (0x8E), e.g., -9223372036854775808
        self.int64TextStream = BytesIO(b"\x8e\x80\x00\x00\x00\x00\x00\x00\x00")
        self.int64TextString = -9223372036854775808

        # FloatText record (0x90), e.g., 1.1
        self.floatTextStream = BytesIO(b"\x90\x3f\x8c\xcc\xcd")
        self.floatTextString = 1.1

        # DoubleText record (0x92), e.g., 2.718281828459045
        self.doubleTextStream = BytesIO(b"\x92\x40\x05\xbf\x0a\x8b\x14\x57\x74")
        self.doubleTextString = 2.7182818284590451

        # DecimalText record (0x94), e.g., 5.123456
        self.decimalTextStream = BytesIO(
            b"\x94\x00\x00\x00\x00\x04\xf2\xd8\x00\x00\x00\x00\x00\x00\x06\x00\x00"
        )
        self.decimalTextString = 5.123456

        # DateTimeText record (0x96)
        self.dateTimeTextStream = BytesIO(b"\x96#\t\x088K\xc0\xf0\x00")
        self.dateTimeTextString = "2001-01-01T13:30:00"

        # Chars8Text record (0x98)
        self.chars8TextStream = BytesIO(b"\x98\x03\x41\x42\x43")
        self.chars8TextString = "ABC"

        # Chars16Text record (0x9A)
        self.chars16TextStream = BytesIO(b"\x9a\x03\x41\x42\x43")
        self.chars16TextString = "ABC"

        # Chars32Text record (0x9C)
        self.chars32TextStream = BytesIO(b"\x9c\x03\x41\x42\x43")
        self.chars32TextString = "ABC"

        # Bytes8Text record (0x9E)
        self.bytes8TextStream = BytesIO(b"\x9e\x03\x01\x02\x03")
        self.bytes8TextString = "AQID"  # Base64 of {0x01, 0x02, 0x03}

        # Bytes16Text record (0xA0)
        self.bytes16TextStream = BytesIO(b"\xa0\x03\x01\x02\x03")
        self.bytes16TextString = "AQID"  # Base64 of {0x01, 0x02, 0x03}

        # Bytes16Text record (0xA2)
        self.bytes32TextStream = BytesIO(b"\xa0\x03\x01\x02\x03")
        self.bytes32TextString = "AQID"  # Base64 of {0x01, 0x02, 0x03}

        # StartListText record (0xA4) with nested text records
        self.startListStream = BytesIO(b"\xa4\x86\x84\x80\x82\xa6")
        self.startListString = "true false 0 1"

        # StartListText record (0xA4) with nested text records
        self.endListStream = BytesIO(b"\xa4\x86\x84\x80\x82\xa6")
        self.endListString = "true false 0 1"

        # EmptyText record (0xA8)
        self.emptyTextStream = BytesIO(b"\xa8")
        self.emptyTextString = ""

        self.dictionaryTextStream = BytesIO(b"\xaa\x08")
        self.dictionaryTextString = "Header"

        # UniqueIdText record (0xAC) with a mock UUID
        self.uniqueIdStream = BytesIO(
            b"\xac\x33\x22\x11\x00\x55\x44\x77\x66\x88\x99\xaa\xbb\xcc\xdd\xee\xff"
        )
        self.uniqueIdString = "urn:uuid:33221100-5544-7766-8899-aabbccddeeff"

        # TimeSpanText record (0xAE) for 1 hour (36000000000 in 100 nanoseconds)
        self.timeSpanStream = BytesIO(
            b"\xae\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00"
        )
        self.timeSpanString = "00:00:01"

        # UuidText record (0xB0) with a mock UUID
        self.uuidStream = BytesIO(
            b"\xb0\x33\x22\x11\x00\x55\x44\x77\x66\x88\x99\xaa\xbb\xcc\xdd\xee\xff"
        )
        self.uuidString = "33221100-5544-7766-8899-aabbccddeeff"

        # UInt64Text record (0xB2) with maximum unsigned 64-bit integer value
        self.uint64Stream = BytesIO(b"\xb2\xff\xff\xff\xff\xff\xff\xff\xff")
        self.uint64String = "18446744073709551615"

        # BoolText record (0xB4) with true
        self.boolTrueStream = BytesIO(b"\xb4\x01")
        self.boolTrueString = "true"

        # BoolText record (0xB4) with false
        self.boolFalseStream = BytesIO(b"\xb4\x00")
        self.boolFalseString = "false"

        # UnicodeChars8Text record (0xB6)
        self.unicodeChars8Stream = BytesIO(b"\xb6\x08\xff\xfea\x00b\x00c\x00")
        self.unicodeChars8String = "abc"

        # UnicodeChars16Text record (0xB8)
        self.unicodeChars16Stream = BytesIO(b"\xb6\x08\xff\xfea\x00b\x00c\x00")
        self.unicodeChars16String = "abc"

        # UnicodeChars32Text record (0xBA)
        self.unicodeChars32Stream = BytesIO(b"\xb6\x08\xff\xfea\x00b\x00c\x00")
        self.unicodeChars32String = "abc"

        # QNameDictionaryTextRecord (0xBC)
        self.qnameDictStream = BytesIO(b"\xbc\x01\x6e")
        self.qnameDictString = "b:Expires"

    def test_zero_text(self):
        result = text_parser()(self.zeroTextStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.zeroTextString, result.unwrap())

    def test_one_text(self):
        result = text_parser()(self.oneTextStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.oneTextString, result.unwrap())

    def test_false_text(self):
        result = text_parser()(self.falseTextStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.falseTextString, result.unwrap())

    def test_true_text(self):
        result = text_parser()(self.trueTextStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.trueTextString, result.unwrap())

    def test_int8_text(self):
        result = text_parser()(self.int8TextStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.int8TextString, result.unwrap())

    def test_int16_text(self):
        result = text_parser()(self.int16TextStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.int16TextString, result.unwrap())

    def test_int32_text(self):
        result = text_parser()(self.int32TextStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.int32TextString, result.unwrap())

    def test_int64_text(self):
        result = text_parser()(self.int64TextStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.int64TextString, result.unwrap())

    def test_float_text(self):
        result = text_parser()(self.floatTextStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.floatTextString, result.unwrap())

    def test_double_text(self):
        result = text_parser()(self.doubleTextStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.doubleTextString, result.unwrap())

    def test_decimal_text(self):
        result = text_parser()(self.decimalTextStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.decimalTextString, result.unwrap())

    def test_date_time_text(self):
        result = text_parser()(self.dateTimeTextStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.dateTimeTextString, result.unwrap())

    def test_chars8_text(self):
        result = text_parser()(self.chars8TextStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.chars8TextString, result.unwrap())

    def test_chars16_text(self):
        result = text_parser()(self.chars16TextStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.chars16TextString, result.unwrap())

    def test_chars32_text(self):
        result = text_parser()(self.chars32TextStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.chars32TextString, result.unwrap())

    def test_bytes8_text(self):
        result = text_parser()(self.bytes8TextStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.bytes8TextString, result.unwrap())

    def test_bytes16_text(self):
        result = text_parser()(self.bytes16TextStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.bytes16TextString, result.unwrap())

    def test_bytes32_text(self):
        result = text_parser()(self.bytes32TextStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.bytes32TextString, result.unwrap())

    def test_start_list_text(self):
        result = text_parser()(self.startListStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.startListString, result.unwrap())

    def test_end_list_text(self):
        result = text_parser()(self.endListStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.endListString, result.unwrap())

    def test_empty_text(self):
        result = text_parser()(self.emptyTextStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.emptyTextString, result.unwrap())

    def test_dictionary_text(self):
        result = text_parser()(self.dictionaryTextStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.dictionaryTextString, result.unwrap())

    def test_unique_id_text(self):
        result = text_parser()(self.uniqueIdStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.uniqueIdString, result.unwrap())

    def test_time_span_text(self):
        result = text_parser()(self.timeSpanStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.timeSpanString, result.unwrap())

    def test_uuid_text(self):
        result = text_parser()(self.uuidStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.uuidString, result.unwrap())

    def test_uint64_text(self):
        result = text_parser()(self.uint64Stream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.uint64String, result.unwrap())

    def test_bool_true_text(self):
        result = text_parser()(self.boolTrueStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.boolTrueString, result.unwrap())

    def test_bool_false_text(self):
        result = text_parser()(self.boolFalseStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.boolFalseString, result.unwrap())

    def test_unicode_chars_8_text(self):
        result = text_parser()(self.unicodeChars8Stream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.unicodeChars8String, result.unwrap())

    def test_unicode_chars_16_text(self):
        result = text_parser()(self.unicodeChars16Stream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.unicodeChars16String, result.unwrap())

    def test_unicode_chars_32_text(self):
        result = text_parser()(self.unicodeChars32Stream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.unicodeChars32String, result.unwrap())

    def test_qname_dictionary_text(self):
        result = text_parser()(self.qnameDictStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.qnameDictString, result.unwrap())
