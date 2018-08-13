import json
from datetime import datetime

import collections
from typing import Optional, List, Dict, Callable, Any, NewType

from ajson.json_class_reports import JsonClassReports, _ClassReport, _AttrReport

Groups = NewType("Groups", Optional[List[str]])
Handler = NewType("Handler", Callable[[Any, Groups, _AttrReport], Any])


class Serializer:
    def __init__(self, max_depth=15):
        self.max_depth: int = max_depth
        self._handlers: Dict[type, Handler] = {}

    def add_handler(self, _class: type, handler: Handler):
        self._handlers[_class] = handler

    def serialize(self, obj, groups: Optional[List[str]] = None):
        return json.dumps(self.to_dict(obj, groups, 0))

    def to_dict(self, obj, groups: Optional[List[str]] = None, _depth=0, attr_report: _AttrReport = None):
        _depth += 1
        if _depth > self.max_depth:
            return "..."
        for class_ in self._handlers:
            if isinstance(obj, class_):
                return self.to_dict(self._handlers[class_](obj, groups, attr_report), groups, _depth)
        if obj is None:
            return None
        elif isinstance(obj, (int, str, float)):
            return obj
        elif isinstance(obj, datetime):
            return self.__datetime_handler(obj, attr_report)
        elif isinstance(obj, (list, tuple, set)):
            return self.__list_handler(obj, _depth)
        elif isinstance(obj, dict):
            return self.__dict_handler(obj,  groups, _depth)
        else:
            return self.__object_handler(obj, groups, _depth)

    def __list_handler(self, obj: list, depth):
        serialized_list = []
        obj = list(obj)
        for item in obj:
            serialized_list.append(self.to_dict(item, depth))
        return serialized_list

    def __dict_handler(self, obj: dict, groups: Optional[List[str]], depth,
                       class_report: Optional[_ClassReport] = None):
        serialized_dict = {}
        for key, value in obj.items():
            if class_report is None:
                attr_report = None
            else:
                attr_report = class_report.get(key)
            serialized_dict[key] = self.to_dict(value, groups, depth, attr_report)
        return serialized_dict

    def __datetime_handler(self, obj: datetime, attr_report: Optional[_AttrReport] = None) -> str:
        if attr_report is None:
            return obj.isoformat()

        return obj.strftime(attr_report.datetime_format)

    def __object_handler(self, obj: object, groups: Optional[List[str]], depth):
        attributes = {key: value for key, value in obj.__dict__.items()
                      if not isinstance(value, collections.Callable) and
                      not "key".startswith("_")}
        class_report = JsonClassReports().reports.get(obj.__class__, None)
        if class_report is None:
            return self.__dict_handler(attributes, groups, depth)
        attributes_to_serialize = class_report.get_attribute_names(groups)

        attributes = {key: val for key, val in attributes.items() if key in attributes_to_serialize}
        return self.__dict_handler(attributes, groups, depth, class_report)

    def unserialize(self, message_str):
        return self.from_dict(json.loads(message_str))

    def from_dict(self, obj):
        if isinstance(obj, (list, tuple, set)):
            return [self.from_dict(item) for item in obj]
        elif isinstance(obj, dict):
            if self.DATE_TAME_KEY in obj:
                return datetime.utcfromtimestamp(obj[self.DATE_TAME_KEY]/1000.0)
            return {key: self.from_dict(item) for key, item in obj.items()}
        return obj