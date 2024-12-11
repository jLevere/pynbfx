from io import BytesIO
from unittest import TestCase
from xml.etree import ElementTree as ET

from pynbfx.records import (
    element_parser,
)


class TestLargeRealDataParsing(TestCase):
    def setUp(self) -> None:
        self.usersRequestResponseStream = BytesIO(
            b'V\x02\x0b\x01s\x04\x0b\x01a\x06V\x08D\n\x1e\x00\x82\x99>http://schemas.xmlsoap.org/ws/2004/09/enumeration/PullResponseD\x12\xad \xcf\x9a\xba\x9b)\xc0D\xbb\x9c\xc8\x8d\xdcp\xf6\xbb@\nActivityId\x04\rCorrelationId\x98$988d6de0-ca59-4bc4-ae38-52848acac5ff\x08=http://schemas.microsoft.com/2004/09/ServiceModel/Diagnostics\xb1\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00D\x0c\x1e\x00\x82\xab\x14\x01V\x0eA\x04wsen\x0cPullResponse\t\x04wsen1http://schemas.xmlsoap.org/ws/2004/09/enumeration\t\x03xsd http://www.w3.org/2001/XMLSchema\t\x03xsi)http://www.w3.org/2001/XMLSchema-instance\t\x06addata8http://schemas.microsoft.com/2008/1/ActiveDirectory/Data\t\x02ad3http://schemas.microsoft.com/2008/1/ActiveDirectoryA\x04wsen\x05ItemsA\x06addata\x04userA\x02ad\x17objectReferencePropertyA\x02ad\x05value\x05\x03xsi\x04type\x98\nxsd:string\x99$7ace7909-563a-4565-b902-8fb346275823\x01A\x06addata\x11distinguishedName\x04\nLdapSyntax\x98\nDSDNStringA\x02ad\x05value\x05\x03xsi\x04type\x98\nxsd:string\x99-CN=Administrator,CN=Users,DC=fmradio,DC=local\x01A\x06addata\tobjectSid\x04\nLdapSyntax\x98\tSidStringA\x02ad\x05value\x05\x03xsi\x04type\x98\x10xsd:base64Binary\x9e\x1b\x01\x05\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00l\xc4\xc4\x9f\xa2\xfb"0\xb0\xadm(\xf4\x01\x00\x9f\x01\x00\x01A\x06addata\x0esAMAccountName\x04\nLdapSyntax\x98\rUnicodeStringA\x02ad\x05value\x05\x03xsi\x04type\x98\nxsd:string\x99\rAdministrator\x01\x01A\x06addata\x04userA\x02ad\x17objectReferencePropertyA\x02ad\x05value\x05\x03xsi\x04type\x98\nxsd:string\x99$e2fc86a8-16e5-40b5-a7cb-54f275ca9c51\x01A\x06addata\x11distinguishedName\x04\nLdapSyntax\x98\nDSDNStringA\x02ad\x05value\x05\x03xsi\x04type\x98\nxsd:string\x99%CN=Guest,CN=Users,DC=fmradio,DC=local\x01A\x06addata\tobjectSid\x04\nLdapSyntax\x98\tSidStringA\x02ad\x05value\x05\x03xsi\x04type\x98\x10xsd:base64Binary\x9e\x1b\x01\x05\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00l\xc4\xc4\x9f\xa2\xfb"0\xb0\xadm(\xf5\x01\x00\x9f\x01\x00\x01A\x06addata\x0esAMAccountName\x04\nLdapSyntax\x98\rUnicodeStringA\x02ad\x05value\x05\x03xsi\x04type\x98\nxsd:string\x99\x05Guest\x01\x01A\x06addata\x04userA\x02ad\x17objectReferencePropertyA\x02ad\x05value\x05\x03xsi\x04type\x98\nxsd:string\x99$726169ee-fc88-46d0-8ac0-4879463e33cf\x01A\x06addata\x11distinguishedName\x04\nLdapSyntax\x98\nDSDNStringA\x02ad\x05value\x05\x03xsi\x04type\x98\nxsd:string\x99&CN=krbtgt,CN=Users,DC=fmradio,DC=local\x01A\x06addata\tobjectSid\x04\nLdapSyntax\x98\tSidStringA\x02ad\x05value\x05\x03xsi\x04type\x98\x10xsd:base64Binary\x9e\x1b\x01\x05\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00l\xc4\xc4\x9f\xa2\xfb"0\xb0\xadm(\xf6\x01\x00\x9f\x01\x00\x01A\x06addata\x0esAMAccountName\x04\nLdapSyntax\x98\rUnicodeStringA\x02ad\x05value\x05\x03xsi\x04type\x98\nxsd:string\x99\x06krbtgt\x01\x01A\x06addata\x04userA\x02ad\x17objectReferencePropertyA\x02ad\x05value\x05\x03xsi\x04type\x98\nxsd:string\x99$fb7deac0-a5fb-4875-8888-034f6f8927a8\x01A\x06addata\x11distinguishedName\x04\nLdapSyntax\x98\nDSDNStringA\x02ad\x05value\x05\x03xsi\x04type\x98\nxsd:string\x99(CN=testacc1,CN=Users,DC=fmradio,DC=local\x01A\x06addata\tobjectSid\x04\nLdapSyntax\x98\tSidStringA\x02ad\x05value\x05\x03xsi\x04type\x98\x10xsd:base64Binary\x9e\x1b\x01\x05\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00l\xc4\xc4\x9f\xa2\xfb"0\xb0\xadm(O\x04\x00\x9f\x01\x00\x01A\x06addata\x0esAMAccountName\x04\nLdapSyntax\x98\rUnicodeStringA\x02ad\x05value\x05\x03xsi\x04type\x98\nxsd:string\x99\x08testacc1\x01\x01\x01A\x04wsen\rEndOfSequence\x01\x01\x01\x01'
        )
        self.usersRequestResponseString = """
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:a="http://www.w3.org/2005/08/addressing">
    <s:Header>
        <a:Action s:mustUnderstand="1">http://schemas.xmlsoap.org/ws/2004/09/enumeration/PullResponse</a:Action>
        <a:RelatesTo>urn:uuid:ccd003ad-cbe2-43f0-b97b-e4a5c073490f</a:RelatesTo>
        <ActivityId CorrelationId="57e62b8f-a16f-434e-a96a-5c192e3d538b" xmlns="http://schemas.microsoft.com/2004/09/ServiceModel/Diagnostics">00000000-0000-0000-0000-000000000000</ActivityId>
        <a:To s:mustUnderstand="1">http://www.w3.org/2005/08/addressing/anonymous</a:To>
    </s:Header>
    <s:Body>
        <wsen:PullResponse xmlns:wsen="http://schemas.xmlsoap.org/ws/2004/09/enumeration" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:addata="http://schemas.microsoft.com/2008/1/ActiveDirectory/Data" xmlns:ad="http://schemas.microsoft.com/2008/1/ActiveDirectory">
            <wsen:Items>
                <addata:user>
                    <ad:objectReferenceProperty>
                        <ad:value xsi:type="xsd:string">7ace7909-563a-4565-b902-8fb346275823</ad:value>
                    </ad:objectReferenceProperty>
                    <addata:distinguishedName LdapSyntax="DSDNString">
                        <ad:value xsi:type="xsd:string">CN=Administrator,CN=Users,DC=fmradio,DC=local</ad:value>
                    </addata:distinguishedName>
                    <addata:objectSid LdapSyntax="SidString">
                        <ad:value xsi:type="xsd:base64Binary">AQUAAAAAAAUVAAAAbMTEn6L7IjCwrW0o9AEAAA==</ad:value>
                    </addata:objectSid>
                    <addata:sAMAccountName LdapSyntax="UnicodeString">
                        <ad:value xsi:type="xsd:string">Administrator</ad:value>
                    </addata:sAMAccountName>
                </addata:user>
                <addata:user>
                    <ad:objectReferenceProperty>
                        <ad:value xsi:type="xsd:string">e2fc86a8-16e5-40b5-a7cb-54f275ca9c51</ad:value>
                    </ad:objectReferenceProperty>
                    <addata:distinguishedName LdapSyntax="DSDNString">
                        <ad:value xsi:type="xsd:string">CN=Guest,CN=Users,DC=fmradio,DC=local</ad:value>
                    </addata:distinguishedName>
                    <addata:objectSid LdapSyntax="SidString">
                        <ad:value xsi:type="xsd:base64Binary">AQUAAAAAAAUVAAAAbMTEn6L7IjCwrW0o9QEAAA==</ad:value>
                    </addata:objectSid>
                    <addata:sAMAccountName LdapSyntax="UnicodeString">
                        <ad:value xsi:type="xsd:string">Guest</ad:value>
                    </addata:sAMAccountName>
                </addata:user>
                <addata:user>
                    <ad:objectReferenceProperty>
                        <ad:value xsi:type="xsd:string">726169ee-fc88-46d0-8ac0-4879463e33cf</ad:value>
                    </ad:objectReferenceProperty>
                    <addata:distinguishedName LdapSyntax="DSDNString">
                        <ad:value xsi:type="xsd:string">CN=krbtgt,CN=Users,DC=fmradio,DC=local</ad:value>
                    </addata:distinguishedName>
                    <addata:objectSid LdapSyntax="SidString">
                        <ad:value xsi:type="xsd:base64Binary">AQUAAAAAAAUVAAAAbMTEn6L7IjCwrW0o9gEAAA==</ad:value>
                    </addata:objectSid>
                    <addata:sAMAccountName LdapSyntax="UnicodeString">
                        <ad:value xsi:type="xsd:string">krbtgt</ad:value>
                    </addata:sAMAccountName>
                </addata:user>
                <addata:user>
                    <ad:objectReferenceProperty>
                        <ad:value xsi:type="xsd:string">fb7deac0-a5fb-4875-8888-034f6f8927a8</ad:value>
                    </ad:objectReferenceProperty>
                    <addata:distinguishedName LdapSyntax="DSDNString">
                        <ad:value xsi:type="xsd:string">CN=testacc1,CN=Users,DC=fmradio,DC=local</ad:value>
                    </addata:distinguishedName>
                    <addata:objectSid LdapSyntax="SidString">
                        <ad:value xsi:type="xsd:base64Binary">AQUAAAAAAAUVAAAAbMTEn6L7IjCwrW0oTwQAAA==</ad:value>
                    </addata:objectSid>
                    <addata:sAMAccountName LdapSyntax="UnicodeString">
                        <ad:value xsi:type="xsd:string">testacc1</ad:value>
                    </addata:sAMAccountName>
                </addata:user>
            </wsen:Items>
            <wsen:EndOfSequence></wsen:EndOfSequence>
        </wsen:PullResponse>
    </s:Body>
</s:Envelope>
        """

    def elem_to_str(self, root: ET.Element) -> str:
        return ET.tostring(root, short_empty_elements=False, encoding="unicode")

    def test_users_request_reponse(self):
        result = element_parser()(self.usersRequestResponseStream)
        self.assertTrue(result.is_ok())
        with open("dump.txt", "w+") as f:
            f.write(self.usersRequestResponseString.replace("\n", "").replace(" ", ""))
            f.write("\n")
            f.write(self.elem_to_str(result.unwrap()).replace(" ", ""))
        self.assertEqual(
            self.usersRequestResponseString.replace("\n", ""),
            self.elem_to_str(result.unwrap()),
        )
