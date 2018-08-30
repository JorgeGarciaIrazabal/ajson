import json
from typing import Dict, List, Optional, Set, Type

from typeguard import check_type

from ajson.singleton import Singleton

ISO_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'


class AJsonAnnotationParseError(Exception):
    pass


class AJsonValidationError(TypeError):
    pass


class AJsonEmptyRequiredAttributeError(AJsonValidationError):
    pass


class _AttrReport(object):
    def __init__(self, attribute_name: str, hint: Optional[Type], **kwargs):
        self.groups: Optional[Set[str]] = kwargs.get('groups', None)
        self.name: str = kwargs.get('name', attribute_name)
        self.datetime_format: str = kwargs.get('d_format', ISO_FORMAT)  # iso format
        self.attribute_name: str = attribute_name
        self.required: str = kwargs.get('required', 'false')

        self.hint: Type = hint

        if self.groups is not None:
            self.groups = set(json.loads(self.groups))
            for group in self.groups:
                if not isinstance(group, (str, int)):
                    raise AJsonAnnotationParseError('unable to parse groups for attribute "{}"'.format(attribute_name))
        self.required = self.required.lower() != 'false'


class _TypeReport(object):
    def __init__(self, attr_reports: Dict[str, _AttrReport], hint: Type):
        self.report_map: Dict[str, _AttrReport] = attr_reports
        self.hint = hint

    def get(self, attr_name: str) -> _AttrReport:
        return self.report_map[attr_name]

    def get_attribute_names(self, groups: Optional[List[str]] = None) -> List[str]:
        if groups is None:
            return list(self.report_map.keys())
        return [
            key for key, report in self.report_map.items()
            if report.groups is None or
               len(report.groups.intersection(groups)) > 0
        ]

    def get_by_serialize_name_or_default(self, name: str) -> _AttrReport:
        try:
            return next(x for x in self.report_map.values() if x.name == name)
        except StopIteration:
            return _AttrReport(name, hint=None)

    # todo move this function to the serializer, it doesn't make sense to have this in a report
    def validate_instance(self, instance):
        for key, report in self.report_map.items():
            if hasattr(instance, report.attribute_name) and getattr(instance, report.attribute_name) is not None:
                value = getattr(instance, report.attribute_name)
                if report.hint is not None:
                    try:
                        check_type(report.attribute_name, value, report.hint)
                    except TypeError:
                        error_text = 'attribute: "{0}.{1}" do not have type: {2}'
                        error_text_params = self.hint.__name__, report.attribute_name, report.hint
                        raise AJsonValidationError(error_text.format(*error_text_params))

            elif report.required:
                error_text = 'required attribute: "{0}.{1}" is empty'
                raise AJsonEmptyRequiredAttributeError(error_text.format(self.hint.__name__, report.attribute_name))


class JsonTypeReports(object, metaclass=Singleton):
    def __init__(self):
        self.reports: Dict[type, _TypeReport] = {}

    def add(self, _type: Type, type_report_dict: Dict):
        type_report = {}
        for key, attribute_report in type_report_dict.items():
            type_report[key] = _AttrReport(key, hint=None, **attribute_report)

        # adding extra reports for the attributes that have a type but not a @aj annotation
        if hasattr(_type, '__annotations__'):
            for key, attr_hint in _type.__annotations__.items():
                type_report[key] = type_report.get(key, _AttrReport(key, hint=None))
                type_report[key].hint = attr_hint

        self.reports[_type] = _TypeReport(type_report, _type)

        # merge parent report with the new one
        for parent_class in _type.__bases__:
            if parent_class in self.reports:
                self.reports[_type].report_map = {**self.reports[parent_class].report_map,
                                                  **self.reports[_type].report_map}

    def clear(self):
        self.reports = {}
