import inspect
import json
import re
from typing import Dict, Pattern, Match, Optional

from _comment_handler import CommentHandler
from regex import as_comment_regex, find_attribute_regex
from singleton import Singleton


class ClassInspector(object, metaclass=Singleton):

    def inspect_class(self, _class) -> Dict[str, Dict]:
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
                as_params_dict = json.loads(as_str[3:])
                attribute = self._find_attribute(source, matches.start())
                if attribute is not None:
                    report[attribute] = as_params_dict
            except Exception as e:
                # todo handle this exception
                print(e)
            source = source[matches.end():]
        return report

    def _find_attribute(self, source, as_position) -> Optional[str]:
        source_to_as = source[:as_position]
        line = source_to_as[source_to_as.rfind("\n"):].strip()  # type: str
        attributes_found = find_attribute_regex.findall(line)
        if len(attributes_found) >= 1:
            return attributes_found[0][5:]
        return None

