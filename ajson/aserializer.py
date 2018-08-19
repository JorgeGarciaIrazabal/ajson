import json
from datetime import datetime

import collections
from typing import Optional, List, Dict, Callable, Any, NewType, Type

from ajson.json_class_reports import JsonClassReports, _ClassReport, _AttrReport

Groups = NewType("Groups", Optional[List[str]])
Handler = NewType("Handler", Callable[[Any, Groups, _AttrReport], Any])


class ASerializer:
    def __init__(self, max_depth=15):
        self.max_depth: int = max_depth
        self._handlers: Dict[type, Handler] = {}

    def add_handler(self, _class: type, handler: Handler):
        self._handlers[_class] = handler

    def serialize(self, obj, groups: Optional[List[str]] = None):
        return json.dumps(self.to_dict_recursive(obj, groups, 0))

    def to_dict(self, obj, groups: Optional[List[str]] = None):
        return self.to_dict_recursive(obj, groups, 0)

    def to_dict_recursive(self, obj, groups: Optional[List[str]] = None, _depth=0, attr_report: _AttrReport = None):
        _depth += 1
        if _depth > self.max_depth:
            return "..."
        for class_ in self._handlers:
            if isinstance(obj, class_):
                return self.to_dict_recursive(self._handlers[class_](obj, groups, attr_report), groups, _depth)
        if obj is None:
            return None
        elif isinstance(obj, (int, str, float)):
            return obj
        elif isinstance(obj, datetime):
            return self.__datetime_handler(obj, attr_report)
        elif isinstance(obj, (list, tuple, set)):
            return self.__list_handler(obj, _depth)
        elif isinstance(obj, dict):
            return self.__dict_handler(obj, groups, _depth)
        else:
            return self.__object_handler(obj, groups, _depth)

    def __list_handler(self, obj: list, depth):
        serialized_list = []
        obj = list(obj)
        for item in obj:
            serialized_list.append(self.to_dict_recursive(item, _depth=depth))
        return serialized_list

    def __dict_handler(self,
                       obj: dict,
                       groups: Optional[List[str]],
                       depth,
                       class_report: Optional[_ClassReport] = None
                       ):
        serialized_dict = {}
        for key, value in obj.items():
            if class_report is None:
                attr_report = None
            else:
                attr_report = class_report.get(key)
            serialized_dict[key] = self.to_dict_recursive(value, groups, depth, attr_report)
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

    def unserialize(self, message_str: str, obj: Any) -> Any:
        return self.from_dict(json.loads(message_str), obj)

    def from_dict(self, dict_obj: Dict, _class: Optional[Type] = None, *init_args_array, **init_dict_args) -> Any:
        if isinstance(dict_obj, (list, tuple, set)):
            return [self.from_dict(item, _class, *init_args_array, **init_dict_args) for item in dict_obj]
        elif isinstance(dict_obj, dict):
            class_report = JsonClassReports().reports.get(_class, None)
            if class_report is None or _class is None:
                return dict_obj
            result_obj = _class(*init_args_array, **init_dict_args)
            for key, value in dict_obj.items():
                attr_report = class_report.get_by_serialize_name(key)
                setattr(result_obj, attr_report.attribute_name, self.from_dict(value))
            return result_obj
        return dict_obj
