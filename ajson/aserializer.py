import json
from datetime import datetime
import collections
from typing import Optional, List, Dict, Callable, Any, NewType, Type, Set, Tuple

from ajson.json_class_reports import JsonClassReports, _ClassReport, _AttrReport, ISO_FORMAT

Groups = NewType("Groups", Optional[List[str]])
Handler = NewType("Handler", Callable[[Any, Groups, _AttrReport], Any])


class AJsonUnserializeError(Exception):
    def __init__(self, obj_name, attr_name):
        message = "Unable to unserialize {0}. Attribute {1} not found".format(obj_name, attr_name)
        super(Exception, self).__init__(message)


class ASerializer:
    def __init__(self, max_depth=15):
        self.max_depth: int = max_depth
        self._handlers: Dict[type, Handler] = {}

    def add_handler(self, _class: type, handler: Handler):
        self._handlers[_class] = handler

    def serialize(self, obj, groups: Optional[List[str]] = None):
        return json.dumps(self._to_dict_recursive(obj, groups, 0))

    def to_dict(self, obj, groups: Optional[List[str]] = None):
        return self._to_dict_recursive(obj, groups, 0)

    def _to_dict_recursive(self, obj, groups: Optional[List[str]] = None, _depth=0, attr_report: _AttrReport = None):
        _depth += 1
        if _depth > self.max_depth:
            return "..."
        for class_ in self._handlers:
            if isinstance(obj, class_):
                return self._to_dict_recursive(self._handlers[class_](obj, groups, attr_report), groups, _depth)
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
            serialized_list.append(self._to_dict_recursive(item, _depth=depth))
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
                key = attr_report.name
            serialized_dict[key] = self._to_dict_recursive(value, groups, depth, attr_report)
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

    def unserialize(self, message_str: str, _class: Optional[Type] = None) -> Any:
        return self.from_dict(json.loads(message_str), _class)

    def from_dict(self, dict_obj: Any, _class: Optional[Type] = None, *init_args_array, **init_dict_args):
        return self._from_dict_recursive(dict_obj, _class, *init_args_array, **init_dict_args)

    def _from_dict_recursive(self, dict_obj: Any, _class: Optional[Type] = None, attr_report: _AttrReport = None,
                             *init_args_array, **init_dict_args) -> Any:
        if isinstance(dict_obj, (list, tuple, set)):
            return self._unserialize_list(_class, dict_obj, init_args_array, init_dict_args)
        elif isinstance(dict_obj, dict):
            return self._unserialize_obj(_class, dict_obj, init_args_array, init_dict_args)
        elif isinstance(dict_obj, str):
            return self._unserialize_str_or_date(attr_report, dict_obj)

        return dict_obj

    def _unserialize_obj(self, _class: Optional[Type], dict_obj: Any, init_args_array, init_dict_args):
        class_report = JsonClassReports().reports.get(_class, None)
        if class_report is None or _class is None:
            return {k: self._from_dict_recursive(v) for k, v in dict_obj.items()}
        result_obj = _class(*init_args_array, **init_dict_args)
        for key, value in dict_obj.items():
            try:
                attr_report = class_report.get_by_serialize_name(key)
                if hasattr(_class, '__annotations__'):
                    attr_class = _class.__annotations__.get(attr_report.attribute_name, None)
                else:
                    attr_class = None
                result_dict = self._from_dict_recursive(value, _class=attr_class, attr_report=attr_report)
                setattr(result_obj, attr_report.attribute_name, result_dict)
            except StopIteration:
                if not hasattr(result_obj, key):
                    raise AJsonUnserializeError(_class.__name__, key)
                setattr(result_obj, key, self._from_dict_recursive(value))
        return result_obj

    def _unserialize_str_or_date(self, attr_report: _AttrReport, dict_obj: Any) -> Any:
        # check if it is a date time
        if attr_report is not None:
            datetime_format = attr_report.datetime_format
        else:
            datetime_format = ISO_FORMAT
        try:
            return datetime.strptime(dict_obj, datetime_format)
        except ValueError:
            return dict_obj

    def _unserialize_list(self, _class: Optional[Type], dict_obj: Any, init_args_array, init_dict_args) -> Any:
        if _class is None:
            return [self._from_dict_recursive(item, _class, *init_args_array, **init_dict_args) for item in dict_obj]
        list_type = None
        if _class is not None and getattr(_class, '__args__', None) is not None and len(_class.__args__) > 0:
            list_type = _class.__args__[0]

        if issubclass(_class, List):
            return [self._from_dict_recursive(item, list_type, *init_args_array, **init_dict_args) for item in dict_obj]
        elif issubclass(_class, Set):
            return {self._from_dict_recursive(item, list_type, *init_args_array, **init_dict_args) for item in dict_obj}
        elif issubclass(_class, Tuple):
            return (self._from_dict_recursive(item, list_type, *init_args_array, **init_dict_args) for item in dict_obj)
        else:
            return [self._from_dict_recursive(item, _class, *init_args_array, **init_dict_args) for item in dict_obj]
