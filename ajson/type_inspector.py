import inspect
import logging
import os
from typing import Dict, Match, Optional

from bs4 import BeautifulSoup

from ajson.comment_handler import CommentHandler
from ajson.regex import as_comment_regex, find_attribute_regex
from ajson.singleton import Singleton


class TypeInspector(object, metaclass=Singleton):

    def inspect_type(self, _class) -> Dict[str, Dict]:
        source = inspect.getsource(_class)
        clean_source = CommentHandler().format_class_source(source)
        return self._get_as_annotation_reports(clean_source)

    def _get_as_annotation_reports(self, source) -> Dict[str, Dict]:
        report = {}  # type: Dict[str, Dict]

        while True:
            matches = as_comment_regex.search(source)  # type: Match
            if matches is None:
                break
            # getting the as string and removing the # in case the json is multi line
            as_str = source[matches.start(): matches.end()].replace("#", "")
            try:
                xml_as_str = "<tag {} ></tag>".format(as_str[4:-1].replace(os.linesep, ''))
                as_params_dict = BeautifulSoup(xml_as_str, features="html.parser").find('tag').attrs
                as_params_dict = {k: v.replace("'", '"') for k, v in as_params_dict.items()}
                attribute = self._find_attribute(source, matches.start())
                if attribute is not None:
                    report[attribute] = as_params_dict
            except Exception as e:
                logging.warning("Unable to parse @aj {}".format(matches[0]))
            source = source[matches.end():]
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
