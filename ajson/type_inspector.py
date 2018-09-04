import inspect
import logging
import os
from typing import AnyStr, Dict, Match, Optional, Type

from bs4 import BeautifulSoup

from ajson.comment_handler import CommentHandler
from ajson.regex import as_comment_regex, find_attribute_regex
from ajson.singleton import Singleton


class TypeInspector(object, metaclass=Singleton):

    def inspect_type(self, _type: Type) -> Dict[str, Dict]:
        source = inspect.getsource(_type)
        clean_source = CommentHandler().format_class_source(source)

        return {
            **self._get_aj_annotation_reports(clean_source),
            **self._get_properties_report(_type)
        }

    def _get_aj_annotation_reports(self, source) -> Dict[str, Dict]:
        report = {}

        while True:
            matches = as_comment_regex.search(source)
            if matches is None:
                break
            try:
                aj_dict = self.aj_str_to_aj_dict(matches)
                attribute = self._find_attribute(source, matches.start())
                if attribute is not None:
                    report[attribute] = aj_dict
            except Exception as e:
                logging.warning("Unable to parse @aj {}".format(matches[0]))
            source = source[matches.end():]

        return report

    def _get_properties_report(self, _type: Type) -> Dict[str, Dict]:
        properties = [(key, value) for key, value in vars(_type).items() if
                      isinstance(value, property) and value.__doc__]

        report = {}
        for name, prop in properties:
            matches = as_comment_regex.search(prop.__doc__)
            if matches is None:
                break
            aj_dict = self.aj_str_to_aj_dict(matches)
            report[name] = aj_dict
        return report

    def _find_attribute(self, source, as_position) -> Optional[str]:
        source_to_as = source[:as_position]
        line: str = source_to_as[source_to_as.rfind("\n"):].strip()
        attributes_found = find_attribute_regex.findall(line)
        if len(attributes_found) >= 1:
            if attributes_found[0][1] == '':
                return attributes_found[0][0][5:]
            else:
                return attributes_found[0][1]

        return None

    def aj_str_to_aj_dict(self, matches: Match[AnyStr]) -> Optional[Dict]:
        # getting the aj string and removing the # in case the json is multi line
        aj_str = matches.string[matches.start(): matches.end()].replace("#", "")
        xml_aj_str = "<tag {} ></tag>".format(aj_str[4:-1].replace(os.linesep, ''))
        aj_params_dict = BeautifulSoup(xml_aj_str, features="html.parser").find('tag').attrs
        return {k: v.replace("'", '"') for k, v in aj_params_dict.items()}
