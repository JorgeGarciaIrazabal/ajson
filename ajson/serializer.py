import json
from datetime import datetime

import collections
from typing import Optional, List

from ajson._json_class_reports import JsonClassReports


class Serializer:
    handlers = {}
    DATE_TAME_KEY = "__date_time__"
    __epoch = datetime.utcfromtimestamp(0)

    def __init__(self, max_depth=15):
        self.max_depth = max_depth

    def serialize(self, obj, groups: Optional[List[str]] = None):
        return json.dumps(self.to_dict(obj, groups, 0))

    def to_dict(self, obj, groups: Optional[List[str]] = None, _depth=0):
        handled_types = self.handlers.keys()
        _depth += 1
        if _depth > self.max_depth:
            return "..."
        for class_ in handled_types:
            if isinstance(obj, class_):
                return self.to_dict(self.handlers[class_](obj, _depth), groups, _depth)
        if obj is None:
            return None
        elif isinstance(obj, (int, str, float)):
            return obj
        elif isinstance(obj, datetime):
            return self.__datetime_handler(obj)
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

    def __dict_handler(self, obj: dict, groups: Optional[List[str]], depth):
        serialized_dict = {}
        for key, value in obj.items():
            serialized_dict[key] = self.to_dict(value, groups, depth)
        return serialized_dict

    def __datetime_handler(self, obj: datetime):
        time_stamp = (obj - self.__epoch).total_seconds() * 1000.0
        return {self.DATE_TAME_KEY: int(time_stamp)}

    def __object_handler(self, obj: object, groups: Optional[List[str]], depth):
        attributes = {key: value for key, value in obj.__dict__.items()
                      if not isinstance(value, collections.Callable) and
                      not "key".startswith("_")}
        class_report = JsonClassReports().reports.get(obj.__class__, None)
        if class_report is None:
            return self.__dict_handler(attributes, groups, depth)
        attributes_to_serialize = class_report.get_attribute_names(groups)

        attributes = {key: val for key, val in attributes.items() if key in attributes_to_serialize}
        return self.__dict_handler(attributes, groups, depth)

    def unserialize(self, message_str):
        return self.__unjsonize(json.loads(message_str))

    def __unjsonize(self, obj):
        if isinstance(obj, (list, tuple, set)):
            return [self.__unjsonize(item) for item in obj]
        elif isinstance(obj, dict):
            if self.DATE_TAME_KEY in obj:
                return datetime.utcfromtimestamp(obj[self.DATE_TAME_KEY]/1000.0)
            return {key: self.__unjsonize(item) for key, item in obj.items()}
        return obj