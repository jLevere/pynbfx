from io import BytesIO
from unittest import TestCase
from xml.etree import ElementTree as ET

from pynbfx.records import (
    attribute_parser,
    element_parser,
)


class TestElementRecursive(TestCase):
    def setUp(self) -> None:
        self.shortElementinShortElementStream = BytesIO(
            b"A\x01a\x05testAA\x01a\x04test\x01\x01"
        )
        self.shortElementinShortElementString = "<a:testA><a:test></a:test></a:testA>"

        self.shortElementinShortElementChar32Stream = BytesIO(
            b"A\x01a\x04testA\x01a\x04test\x9c\x03\x41\x42\x43\x01\x01"
        )
        self.shortElementinShortElementChar32String = (
            "<a:test><a:test>ABC</a:test></a:test>"
        )

        self.twoshortElementinShortElementStream = BytesIO(
            b"A\x01a\x04testA\x01a\x04test\x01A\x01a\x04test\x01\x01"
        )
        self.twoshortElementinShortElementString = (
            "<a:test><a:test></a:test><a:test></a:test></a:test>"
        )

        self.shortElementinShortElementChar32EndStream = BytesIO(
            b"A\x01a\x04testA\x01a\x04test\x9d\x03\x41\x42\x43\x01"
        )
        self.shortElementinShortElementChar32EndString = (
            "<a:test><a:test>ABC</a:test></a:test>"
        )

        self.shortElementinShortElementChar32EndStream = BytesIO(
            b"A\x01a\x04testA\x01a\x04test\x9d\x03\x41\x42\x43\x01"
        )
        self.shortElementinShortElementChar32EndString = (
            "<a:test><a:test>ABC</a:test></a:test>"
        )

    def elem_to_str(self, root: ET.Element) -> str:
        return ET.tostring(root, short_empty_elements=False, encoding="unicode")

    def test_two_depth_no_attrs_short_element(self):
        result = element_parser()(self.shortElementinShortElementStream)
        self.assertTrue(result.is_ok())
        self.assertEqual(
            self.shortElementinShortElementString, self.elem_to_str(result.unwrap())
        )

    def test_two_depth_no_attrs_short_element_char32(self):
        result = element_parser()(self.shortElementinShortElementStream)
        self.assertTrue(result.is_ok())
        self.assertEqual(
            self.shortElementinShortElementString, self.elem_to_str(result.unwrap())
        )

    def test_two_depth_no_attrs_two_short_element(self):
        """A parent element with two childeren"""
        result = element_parser()(self.shortElementinShortElementStream)
        self.assertTrue(result.is_ok())
        self.assertEqual(
            self.shortElementinShortElementString, self.elem_to_str(result.unwrap())
        )

    def test_two_depth_no_attrs_two_short_element_with_char32_end(self):
        """A parent with a child that uses an end text element"""
        result = element_parser()(self.shortElementinShortElementStream)
        self.assertTrue(result.is_ok())
        self.assertEqual(
            self.shortElementinShortElementString, self.elem_to_str(result.unwrap())
        )


class TestElementsWithAttributes(TestCase):
    def setUp(self):
        self.shortElementShortAttributeStream = BytesIO(
            b"A\x01a\x04test\x04\x04test\x86\x01"
        )
        self.shortElementShortAttributeString = '<a:test test="true"></a:test>'

        self.shortElement2ShortAttributeStream = BytesIO(
            b"A\x01a\x04test\x04\x04test\x86\x04\x04test\x86\x01"
        )
        self.shortElement2ShortAttributeString = (
            '<a:test test="true" test="true"></a:test>'
        )

    def elem_to_str(self, root: ET.Element) -> str:
        return ET.tostring(root, short_empty_elements=False, encoding="unicode")

    def test_short_element_short_attribute(self):
        parser = element_parser()

        result = parser(self.shortElementShortAttributeStream)
        self.assertTrue(result.is_ok())
        self.assertEqual(
            self.shortElementShortAttributeString, self.elem_to_str(result.unwrap())
        )

    def test_short_element_2_short_attribute(self):
        parser = element_parser()

        result = parser(self.shortElementShortAttributeStream)
        self.assertTrue(result.is_ok())
        self.assertEqual(
            self.shortElementShortAttributeString, self.elem_to_str(result.unwrap())
        )


class TestRecursiveElementWithAttributes(TestCase):
    def setUp(self) -> None:
        self.shortElementinShortElementStream = BytesIO(
            b"A\x01a\x04test\x04\x04test\x86A\x01a\x04test\x01\x01"
        )
        self.shortElementinShortElementString = (
            '<a:test test="true"><a:test></a:test></a:test>'
        )

        self.shortElementinShortElmentAttrStream = BytesIO(
            b"A\x01a\x04test\x04\x04test\x86A\x01a\x04test\x9c\x03\x41\x42\x43\x01\x01"
        )
        self.shortElementinShortElmentAttrString = (
            '<a:test test="true"><a:test test="ABC"></a:test></a:test>'
        )

    def elem_to_str(self, root: ET.Element) -> str:
        return ET.tostring(root, short_empty_elements=False, encoding="unicode")

    def test_two_depth_one_short_attr_short_element(self):
        parser = element_parser()

        result = parser(self.shortElementinShortElementStream)
        self.assertTrue(result.is_ok())
        self.assertEqual(
            self.shortElementinShortElementString, self.elem_to_str(result.unwrap())
        )

    # I think the byteio string is just wrong maybe
    def test_two_depth_one_short_attr_short_element_char32(self):
        parser = element_parser()

        result = parser(self.shortElementinShortElmentAttrStream)
        self.assertTrue(result.is_ok())
        self.assertEqual(
            self.shortElementinShortElmentAttrString, self.elem_to_str(result.unwrap())
        )


class TestAttributesWithText(TestCase):
    def setUp(self):
        self.shortAttributeChar32Stream = BytesIO(b"\x04\x04test\x9c\x03\x41\x42\x43")
        self.shortAttributeChar32Dict = {"test": "ABC"}

    def test_short_attr_with_char32(self):
        result = attribute_parser()(self.shortAttributeChar32Stream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.shortAttributeChar32Dict, result.unwrap())


class TestElementWithText(TestCase):
    def setUp(self):
        # 0x40
        self.shortElementChar32Stream = BytesIO(
            b"A\x01a\x04test\x9c\x03\x41\x42\x43\x01"
        )
        self.shortElementChar32String = "<a:test>ABC</a:test>"

        # 0x41
        self.elementChar32Stream = BytesIO(b"@\x08Envelope\x9c\x03\x41\x42\x43")
        self.elementChar32String = "<Envelope>ABC</Envelope>"

        # 0x42
        self.shortDictElementChar32Stream = BytesIO(b"B\x02\x9c\x03\x41\x42\x43")
        self.shortDictElementChar32String = "<Envelope>ABC</Envelope>"

        # 0x43
        self.dictElementChar32Stream = BytesIO(b"C\x01x\x02\x9c\x03\x41\x42\x43")
        self.dictElementChar32String = "<x:Envelope>ABC</x:Envelope>"

        # 0x45
        self.prefixDictElementChar32Stream = BytesIO(b"\x45\x02\x9c\x03\x41\x42\x43")
        self.prefixDictElementChar32String = "<b:Envelope>ABC</b:Envelope>"

        # 0x5E
        self.prefixElementChar32Stream = BytesIO(
            b"\x5e\x08Envelope\x9c\x03\x41\x42\x43"
        )
        self.prefixElementChar32String = "<a:Envelope>ABC</a:Envelope>"

    def elem_to_str(self, root: ET.Element) -> str:
        return ET.tostring(root, short_empty_elements=False, encoding="unicode")

    def test_zero_depth_no_attrs_short_element_with_char32(self):
        result = element_parser()(self.shortElementChar32Stream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(
            self.shortElementChar32String, self.elem_to_str(result.unwrap())
        )

    def test_zero_depth_no_attrs_element_with_char32(self):
        result = element_parser()(self.elementChar32Stream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.elementChar32String, self.elem_to_str(result.unwrap()))

    def test_zero_depth_no_attrs_short_dict_element_with_char32(self):
        result = element_parser()(self.shortDictElementChar32Stream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(
            self.shortDictElementChar32String, self.elem_to_str(result.unwrap())
        )

    def test_zero_depth_no_attrs_dict_element_with_char32(self):
        result = element_parser()(self.dictElementChar32Stream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(
            self.dictElementChar32String, self.elem_to_str(result.unwrap())
        )

    def test_zero_depth_no_attrs_prefix_dict_element_with_char32(self):
        result = element_parser()(self.prefixDictElementChar32Stream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(
            self.prefixDictElementChar32String, self.elem_to_str(result.unwrap())
        )

    def test_zero_depth_no_attrs_prefix_element_with_char32(self):
        result = element_parser()(self.prefixElementChar32Stream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(
            self.prefixElementChar32String, self.elem_to_str(result.unwrap())
        )


class TestElementWithEndText(TestCase):
    def setUp(self):
        # 0x40
        self.shortElementChar32EndStream = BytesIO(
            b"A\x01a\x04test\x9d\x03\x41\x42\x43\x01"
        )
        self.shortElementChar32EndString = "<a:test>ABC</a:test>"

        # 0x41
        self.elementChar32EndStream = BytesIO(b"@\x08Envelope\x9d\x03\x41\x42\x43")
        self.elementChar32EndString = "<Envelope>ABC</Envelope>"

        # 0x42
        self.shortDictElementChar32EndStream = BytesIO(b"B\x02\x9d\x03\x41\x42\x43")
        self.shortDictElementChar32EndString = "<Envelope>ABC</Envelope>"

        # 0x43
        self.dictElementChar32EndStream = BytesIO(b"C\x01x\x02\x9d\x03\x41\x42\x43")
        self.dictElementChar32EndString = "<x:Envelope>ABC</x:Envelope>"

        # 0x45
        self.prefixDictElementChar32EndStream = BytesIO(b"\x45\x02\x9d\x03\x41\x42\x43")
        self.prefixDictElementChar32EndString = "<b:Envelope>ABC</b:Envelope>"

        # 0x5E
        self.prefixElementChar32EndStream = BytesIO(
            b"\x5e\x08Envelope\x9d\x03\x41\x42\x43"
        )
        self.prefixElementChar32EndString = "<a:Envelope>ABC</a:Envelope>"

    def elem_to_str(self, root: ET.Element) -> str:
        return ET.tostring(root, short_empty_elements=False, encoding="unicode")

    def test_zero_depth_no_attrs_short_element_with_char32_end(self):
        result = element_parser()(self.shortElementChar32EndStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(
            self.shortElementChar32EndString, self.elem_to_str(result.unwrap())
        )

    def test_zero_depth_no_attrs_element_with_char32_end(self):
        result = element_parser()(self.elementChar32EndStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(self.elementChar32EndString, self.elem_to_str(result.unwrap()))

    def test_zero_depth_no_attrs_short_dict_element_with_char32_end(self):
        result = element_parser()(self.shortDictElementChar32EndStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(
            self.shortDictElementChar32EndString, self.elem_to_str(result.unwrap())
        )

    def test_zero_depth_no_attrs_dict_element_with_char32_end(self):
        result = element_parser()(self.dictElementChar32EndStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(
            self.dictElementChar32EndString, self.elem_to_str(result.unwrap())
        )

    def test_zero_depth_no_attrs_prefix_dict_element_with_char32_end(self):
        result = element_parser()(self.prefixDictElementChar32EndStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(
            self.prefixDictElementChar32EndString, self.elem_to_str(result.unwrap())
        )

    def test_zero_depth_no_attrs_prefix_element_with_char32_end(self):
        result = element_parser()(self.prefixElementChar32EndStream)
        self.assertTrue(result.is_ok(), result)
        self.assertEqual(
            self.prefixElementChar32EndString, self.elem_to_str(result.unwrap())
        )


class TestLargeDocs(TestCase):
    maxDiff = None

    def setUp(self):
        self.endElementsStream = BytesIO(
            b"V\x02\x0b\x01a\x06\x0b\x01s\x04V\x08D\n\x1e\x00\x82\x99\x06action\x01V\x0e@\tInventory\x81\x01\x01"
        )
        self.endElementsString = """<s:Envelope xmlns:a="http://www.w3.org/2005/08/addressing"
xmlns:s="http://www.w3.org/2003/05/soap-envelope">
<s:Header>
<a:Action s:mustUnderstand="1">action</a:Action>
</s:Header>
<s:Body>
<Inventory>0</Inventory>
</s:Body>
</s:Envelope>"""

    def elem_to_str(self, root: ET.Element) -> str:
        return ET.tostring(root, short_empty_elements=False, encoding="unicode")

    def test_end_element(self):
        result = element_parser()(self.endElementsStream)

        self.assertTrue(result.is_ok())

        with open("dump.txt", "w+") as f:
            f.write(self.endElementsString.replace("\n", ""))
            f.write("\n")
            f.write(self.elem_to_str(result.unwrap()))

        self.assertEqual(
            self.endElementsString.replace("\n", ""), self.elem_to_str(result.unwrap())
        )
