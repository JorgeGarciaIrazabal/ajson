import collections
import json
from datetime import datetime
from typing import Optional, List, Dict, Callable, Any, NewType, Type, Set, Tuple, Union

from ajson.json_type_reports import JsonTypeReports, _TypeReport, _AttrReport, ISO_FORMAT

Groups = NewType('Groups', Optional[List[str]])
Handler = NewType('Handler', Callable[[Any, Groups, _AttrReport], Any])


class ASerializer:
    """
    Serialize and unserialize objects
    """
    max_depth: int
    """
    Defines how many nested objects should be serialized.
    If the object reaches to this point, the result will be replaced by "..."

    >>> serializer = ASerializer(max_depth=2)
    >>> nested_dict = {"d1": {"d2": {"d3": "value deep inside"}}}
    >>> serializer.serialize(nested_dict)
    "{"d1": {"d2": "..." }}"
    """
    def __init__(self, max_depth=15):
        self.max_depth: int = max_depth
        self._handlers: Dict[Type, Handler] = {}

    def add_serialize_handler(self, _type: Type, handler: Handler):
        """
        Adds a handler for a specific type to modify the way it should be serialize

        >>> serializer = ASerializer()
        >>> serializer.add_serialize_handler(int, lambda obj, *args: obj if obj > 0 else 0) # negative ints return 0
        >>> serializer.serialize(5)
        '5'
        >>> serializer.serialize(-6)
        '0'
        """
        self._handlers[_type] = handler

    def serialize(self, obj, groups: Optional[List[str]] = None) -> str:
        """
        Creates a json string from the obj

        :param obj: Object to be serialize
        :param groups: list of groups that determines what attributes should be serialize

        >>> from ajson import AJson
        >>> serializer = ASerializer()
        >>> @AJson()
        ... class House:
        ...    rooms_num: int  # @aj(groups='["public", "owner"]')
        ...    square_meters: int  # @aj(groups='["owner"]')
        ...    def __init__(self, rooms_num, square_meters):
        ...        self.rooms_num = rooms_num
        ...        self.square_meters = square_meters

        >>> serializer.serialize(House(3, 100), groups=['public'])
        '{"room_num": 3}'
        >>> serializer.serialize(House(3, 100), groups=['owner'])
        '{"room_num": 3, "square_meters": 100}'

        """
        return json.dumps(self._to_dict_recursive(obj, groups, 0))

    def to_dict(self, obj, groups: Optional[List[str]] = None) -> Union[Dict[str, Any], List]:
        """
        Same as serialize, but it creates a serializable dict instead of a str

        :param obj: Object to be serialize
        :param groups: list of groups that determines what attributes should be serialize

        >>> from ajson import AJson
        >>> serializer = ASerializer()
        >>> @AJson()
        ... class Car:
        ...    max_speed: float  # @aj(groups='["basic", "detailed"]')
        ...    brand: str  # @aj(groups='["detailed"]')
        ...    def __init__(self, max_speed, brand):
        ...        self.max_speed = max_speed
        ...        self.brand = brand

        >>> serializer.to_dict(Car(140, 'ford'), groups=['basic'])
        {"max_speed": 140}
        >>> serializer.to_dict(Car(140, 'ford'), groups=['detailed'])
        {"max_speed": 140, "brand": 7}

        """
        return self._to_dict_recursive(obj, groups, 0)

    def _to_dict_recursive(self, obj, groups: Optional[List[str]] = None, depth=0, attr_report: _AttrReport = None):
        depth += 1
        if depth > self.max_depth:
            return '...'
        for class_ in self._handlers:
            if isinstance(obj, class_):
                return self._handlers[class_](obj, groups, attr_report)
        if obj is None:
            return None
        elif isinstance(obj, (int, str, float)):
            return obj
        elif isinstance(obj, datetime):
            return self.__datetime_handler(obj, attr_report)
        elif isinstance(obj, (list, tuple, set)):
            return self.__list_handler(obj, groups, depth)
        elif isinstance(obj, dict):
            return self.__dict_handler(obj, groups, depth)
        else:
            return self.__object_handler(obj, groups, depth)

    def __list_handler(self, obj: list, groups: Optional[List[str]], depth: int):
        serialized_list = []
        obj = list(obj)
        for item in obj:
            serialized_list.append(self._to_dict_recursive(item, groups=groups, depth=depth))
        return serialized_list

    def __dict_handler(self,
                       obj: dict,
                       groups: Optional[List[str]],
                       depth,
                       class_report: Optional[_TypeReport] = None
                       ):
        serialized_dict = {}
        for key, value in obj.items():
            # we don't want to serialize private attributes if we don't have a class report
            if class_report is not None or not str(key).startswith('_'):
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
        class_report = JsonTypeReports().reports.get(obj.__class__, None)
        if class_report is None:
            attributes = {key: value for key, value in obj.__dict__.items()
                          if not isinstance(value, collections.Callable) and
                          not 'key'.startswith('_')}
            return self.__dict_handler(attributes, groups, depth)
        attributes_to_serialize = class_report.get_attribute_names(groups)

        attributes = {key: getattr(obj, key) for key in attributes_to_serialize}
        return self.__dict_handler(attributes, groups, depth, class_report)

    def unserialize(self, json_str: str, _type: Optional[Type] = None, *init_args_array, **init_kargs) -> Any:
        """
        Creates an object with the type `_type` from a string
        groups will be ignored for unserialization

        :param json_str: string to be transformed into an object
        :param _type: Resulting type of the object to construct
        :param init_args_array: construct args list to initialize the object with type `_type`
        :param init_kargs: construct args to initialize the object with type `_type`

        >>> from ajson import AJson
        >>> serializer = ASerializer()
        >>> @AJson()
        ... class House:
        ...    rooms_num: int  # @aj()
        ...    square_meters: int  # @aj()

        >>> house: House = serializer.unserialize('{"rooms_num": 1, "square_meters":50}', House)
        >>> house.rooms_num
        1
        >>> house.square_meters
        50
        """
        return self.from_dict(json.loads(json_str), _type, *init_args_array, **init_kargs)

    def from_dict(self, dict_obj: Any, _type: Optional[Type] = None, *init_args_array, **init_kargs) -> Any:
        """
        Creates an object with the type `_type` from a dictionary
        groups will be ignored for unserialization

        :param dict_obj: dict to be transformed into an object
        :param _type: Resulting type of the object to construct
        :param init_args_array: construct args list to initialize the object with type `_type`
        :param init_kargs: construct args to initialize the object with type `_type`

        >>> from ajson import AJson
        >>> serializer = ASerializer()
        >>> @AJson()
        ... class Car:
        ...    max_speed: float  # @aj(')
        ...    brand: str  # @aj()

        >>> car: Car = serializer.from_dict({'max_speed': 100, 'brand': 'Jeep'}, Car)
        >>> car.max_speed
        100
        >>> car.brand
        'Jeep'
        """

        return self._from_dict_recursive(dict_obj, _type, *init_args_array, **init_kargs)

    def _from_dict_recursive(self, dict_obj: Any, _type: Optional[Type] = None, attr_report: _AttrReport = None,
                             *init_args_array, **init_kargs) -> Any:
        if isinstance(dict_obj, (list, tuple, set)):
            return self._unserialize_list(_type, dict_obj, init_args_array, init_kargs)
        elif isinstance(dict_obj, dict):
            return self._unserialize_obj(_type, dict_obj, init_args_array, init_kargs)
        elif isinstance(dict_obj, str):
            return self._unserialize_str_or_date(attr_report, dict_obj)

        return dict_obj

    def _unserialize_obj(self, _type: Optional[Type], dict_obj: Any, init_args_array, init_kargs):
        type_report = JsonTypeReports().reports.get(_type, None)
        if type_report is None or _type is None:
            return {k: self._from_dict_recursive(v) for k, v in dict_obj.items()}
        result_obj = _type(*init_args_array, **init_kargs)
        for key, value in dict_obj.items():
            attr_report = type_report.get_by_serialize_name_or_default(key)
            result_dict = self._from_dict_recursive(value, _type=attr_report.hint, attr_report=attr_report)
            if hasattr(result_obj, attr_report.attribute_name) or attr_report.hint is not None:
                setattr(result_obj, attr_report.attribute_name, result_dict)

        type_report.validate_instance(result_obj)
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

    def _unserialize_list(self, _type: Optional[Type], dict_obj: Any, init_args_array, init_kargs) -> Any:
        if _type is None:
            return [self._from_dict_recursive(item, _type, *init_args_array, **init_kargs) for item in dict_obj]
        list_type = None
        if _type is not None and getattr(_type, '__args__', None) is not None and len(_type.__args__) > 0:
            list_type = _type.__args__[0]

        if issubclass(_type, List):
            return [self._from_dict_recursive(item, list_type, *init_args_array, **init_kargs) for item in dict_obj]
        elif issubclass(_type, Set):
            return {self._from_dict_recursive(item, list_type, *init_args_array, **init_kargs) for item in dict_obj}
        elif issubclass(_type, Tuple):
            return (self._from_dict_recursive(item, list_type, *init_args_array, **init_kargs) for item in dict_obj)
        else:
            return [self._from_dict_recursive(item, _type, *init_args_array, **init_kargs) for item in dict_obj]
