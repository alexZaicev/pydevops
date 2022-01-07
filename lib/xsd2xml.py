import datetime
import os
import random
import string
import time
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod

import rstr
import xmlschema
from lxml import etree

from lib.model import TaskBase


class Xsd2Xml(TaskBase):

    def __init__(self, dir_xsd, dir_xml, optional, validate):
        TaskBase.__init__(self)
        self.dir_xsd = dir_xsd
        self.dir_xml = dir_xml
        self.optional = optional
        self.validate = validate

    def run(self):
        _xsd_d = dict()
        for f_name in os.listdir(self.dir_xsd):
            if not f_name.endswith('.xsd'):
                continue
            _xsd_d[f_name.replace('.xsd', '')] = os.path.join(self.dir_xsd, f_name)

        for name, path in _xsd_d.items():
            xml_gen = XmlGenerator(path, mandatory_only=not self.optional)
            xml = xml_gen.generate()
            xml_tree = etree.fromstring(xml)

            with open(os.path.join(self.dir_xml, '{}.xml'.format(name)), 'w+') as ff:
                _b_xml = etree.tostring(xml_tree, pretty_print=True)
                ff.write(bytes.decode(_b_xml, encoding='UTF-8'))

            if self.validate:
                xml_vld = XmlValidator(path)
                if not xml_vld.validate(xml_tree):
                    print(xml_vld.errors())
                    raise XmlValidationError('Generate {} XML document is not valid'.format(name))

    def close(self):
        pass

    @classmethod
    def get_date(cls, start, end, format, prop):
        stime = time.mktime(time.strptime(start, format))
        etime = time.mktime(time.strptime(end, format))
        ptime = stime + prop * (etime - stime)

        return time.strftime(format, time.localtime(ptime))

    @classmethod
    def get_mixed_string(cls, length):
        return cls.get_string(string.ascii_uppercase + string.digits, length)

    @classmethod
    def get_digits(cls, length):
        return cls.get_string(string.digits, length)

    @classmethod
    def get_string(cls, population, length):
        return ''.join(random.choices(population, k=length))


class DataFacet(ABC):
    @abstractmethod
    def string(self, node_type):
        pass

    @abstractmethod
    def boolean(self, node_type):
        pass

    @abstractmethod
    def gyearmonth(self, node_type):
        pass

    @abstractmethod
    def datetime(self, node_type):
        pass

    @abstractmethod
    def date(self, node_type):
        pass

    @abstractmethod
    def time(self, node_type):
        pass

    @abstractmethod
    def integer(self, node_type):
        pass

    @abstractmethod
    def float(self, node_type):
        pass

    @abstractmethod
    def byte(self, node_type):
        pass

    @abstractmethod
    def decimal(self, node_type):
        pass


class XmlDefaultDataFacet(DataFacet):

    def string(self, nodetype):
        s = ''
        _facets_str = str(nodetype.facets)
        if "Length" in _facets_str:
            lo, up = 0, 0
            for k, facet in nodetype.facets.items():
                if "minLength" in k:
                    lo = facet.value
                elif "maxLength" in k:
                    up = facet.value

            if nodetype.enumeration is not None and len(nodetype.enumeration) > 0:
                lo, up = 0, 0

            if 'enumeration' in k and len(nodetype.enumeration) > 0:
                enm = nodetype.enumeration
                s = enm[random.randrange(0, len(enm))]
            else:
                s = Xsd2Xml.get_mixed_string(random.randrange(lo, up))
            return s

        if "enumeration" in _facets_str:
            enumeration = list(nodetype.facets.values())[0].enumeration
            return enumeration[random.randrange(0, len(enumeration))]

        if "pattern" in _facets_str:
            regexps = list(nodetype.facets.values())[0].regexps
            return rstr.xeger(regexps[0])

        return Xsd2Xml.get_mixed_string(10)

    def boolean(self, nodetype) -> int:
        return random.randrange(0, 1)  # true / false

    def gyearmonth(self, node_type):
        _now = datetime.datetime.now()
        return '{:04d}-{:02d}'.format(_now.year, _now.month)

    def datetime(self, nodetype):
        if nodetype.local_name.startswith('ISO'):
            return datetime.datetime.now().isoformat(timespec='milliseconds')
        return '{}+00:00'.format(datetime.datetime.now().isoformat(timespec='milliseconds'))

    def date(self, nodetype):
        return self.datetime(nodetype).split('T')[0]

    def time(self, nodetype):
        return self.datetime(nodetype).split('T')[1]

    def integer(self, nodetype):  # todo - complete this part
        return random.randrange(0, 10000)

    def float(self, nodetype):  # todo - complete this part
        return random.randrange(0, 1.0)

    def byte(self, nodetype):  # todo - complete this part
        return random.randrange(0, 8)

    def decimal(self, nodetype):
        digit_size, fraction_size = 0, 0
        # print(nodetype.facets)
        for k, facet in nodetype.facets.items():
            if not k is None:
                if "fractionDigits" in k:
                    fraction_size = facet.value
                elif "totalDigits" in k:
                    digit_size = facet.value
        # elif "assertion" in k:            #for xsd 1.1
        #    assertion = facet.path

        if fraction_size > 0:
            _content_part_2 = Xsd2Xml.get_digits(2)
        else:
            _content_part_2 = "0"

        if digit_size > 0:
            if digit_size - fraction_size == 1:
                _content_part_1 = Xsd2Xml.get_digits(random.randrange(1, 2))
            else:
                _content_part_1 = Xsd2Xml.get_digits(random.randrange(1, digit_size - fraction_size))
        else:
            _content_part_1 = "0"

        return _content_part_1 + "." + _content_part_2


class XmlGenerator:
    """
      ``XmlGenerator(schema_file, mandatory_only=False, xmldatafacet=None)``
                - ``schema_file`` - Path to the XSD
                - ``mandatory_only`` - Generate all the fields or just the mandatory ones (minOccurs > 0)
                - ``xmldatafacet`` - Data facet class. If not provided, the default will be used.
      """

    def __init__(self, schema_file, mandatory_only=False, xmldatafacet=None):
        self.schema = xmlschema.XMLSchema(schema_file)
        self.mandatory_only = mandatory_only
        if xmldatafacet is None:
            self.xmldatafacet = XmlDefaultDataFacet()
        else:
            self.xmldatafacet = xmldatafacet

        self.ET = ET
        self.root = None

    def generate(self) -> str:
        for node in self.schema.root_elements:
            if self.mandatory_only and node.occurs[0] < 1: continue
            self.root = ET.Element(node.local_name, xmlns=self.schema.target_namespace)
            self._recur_build(node, self.root, True)

        return ET.tostring(self.root)

    def _recur_build(self, xsdnode, xmlnode, isroot=False) -> None:

        # skip if only mandatory fields
        if self.mandatory_only and xsdnode.occurs[0] < 1: return

        if not isroot:
            xmlnode = ET.SubElement(xmlnode, xsdnode.local_name)

        # simple content
        if xsdnode.type.has_simple_content():
            if xsdnode.type.is_simple():
                xmlnode.text = self._get_random_content(xsdnode.type)
            else:
                xmlnode.text = self._get_random_content(xsdnode.type.content_type)

        # complex types
        else:
            content_type = xsdnode.type.content_type
            # choice
            if content_type.model == "choice":
                selected_node = content_type._group[0]

                # find mandatory element in group
                if self.mandatory_only:
                    for subnode in content_type._group:
                        if subnode.occurs[0] < 1:
                            continue
                        else:
                            selected_node = subnode

                self._recur_build(selected_node, xmlnode)
            else:
                # sequence
                for subnode in content_type._group:
                    if not hasattr(subnode, 'process_contents'):  # xs:element
                        if hasattr(subnode, '_group'):
                            subnode = subnode._group[0]
                        self._recur_build(subnode, xmlnode)
                    else:  # xs:any
                        subnode = ET.SubElement(xmlnode, 'Any')  # any - close with any tag

        # attributes
        _attributes = dict
        if hasattr(xsdnode, "attributes"):
            _attributes = xsdnode.attributes
        else:
            if hasattr(xsdnode.type, "attributes"):
                attributes = xsdnode.type.attributes
        for attr, attr_obj in _attributes.items():
            xmlnode.attrib[attr] = self._get_random_content(attr_obj.type)

    def _get_random_content(self, nodetype) -> str:
        if self.xmldatafacet:
            datatype = nodetype.primitive_type.local_name.lower()
            call_method = getattr(self.xmldatafacet, datatype)
            return str(call_method(nodetype))
        else:
            return ""


class XmlValidator:

    def __init__(self, xsd_path: str):
        xmlschema_doc = etree.parse(xsd_path)
        self.xmlschema = etree.XMLSchema(xmlschema_doc)

    def validate(self, et: etree) -> bool:
        return self.xmlschema.validate(et)

    def errors(self):
        return self.xmlschema.error_log


class XmlValidationError(Exception):
    pass


if __name__ == '__main__':
    __main()
