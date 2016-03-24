# coding=utf-8

from __future__ import unicode_literals

import six

from rest_framework import renderers

from libs.multilingo.utils import MultiLangDict


class XMLRenderer(renderers.XMLRenderer):
    def _to_xml(self, xml, data):
        if isinstance(data, (list, tuple)):
            for item in data:
                xml.startElement("item", {})
                self._to_xml(xml, item)
                xml.endElement("item")
        elif isinstance(data, MultiLangDict):
            for key, value in six.iteritems(data):
                xml.startElement('languageVersion', {'code': key})
                self._to_xml(xml, value)
                xml.endElement('languageVersion')
        else:
            return super(XMLRenderer, self)._to_xml(xml, data)

