import json
from typing import Dict, List, Optional, Set, Type

from ajson.singleton import Singleton

ISO_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'


class AJsonAnnotationParseError(Exception):
    pass

class AJsonEmptyRequiredAttributeError(Exception):
    pass


class _AttrReport(object):
    def __init__(self, attribute_name: str, **kwargs):
        self.groups: Optional[Set[str]] = kwargs.get('groups', None)
        self.name: str = kwargs.get('name', attribute_name)
        self.datetime_format: str = kwargs.get('d_format', ISO_FORMAT)  # iso format
        self.attribute_name: str = attribute_name
        self.required: str = kwargs.get('required', 'false')

        if self.groups is not None:
            self.groups = set(json.loads(self.groups))
            for group in self.groups:
                if not isinstance(group, (str, int)):
                    raise AJsonAnnotationParseError('unable to parse groups for attribute "{}"'.format(attribute_name))
        self.required = self.required.lower() != 'false'


class _TypeReport(object):
    def __init__(self, attr_reports: Dict[str, _AttrReport], _type: Type):
        self.report_map: Dict[str, _AttrReport] = attr_reports
        self.type = _type

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

    def get_by_serialize_name(self, name: str) -> _AttrReport:
        return next(x for x in self.report_map.values() if x.name == name)

    def validate_instance(self, instance):
        for attr in filter(lambda a:  a.required, self.report_map.values()):
            if not hasattr(instance, attr.attribute_name) or not getattr(instance, attr.attribute_name):
                error_text = 'required attribute: "{1}.{0}" is empty'
                raise AJsonEmptyRequiredAttributeError(error_text.format(attr.attribute_name, self.type.__name__))


class JsonTypeReports(object, metaclass=Singleton):
    def __init__(self):
        self.reports: Dict[type, _TypeReport] = {}

    def add(self, _type: type, class_report_dict: Dict):
        class_report = {}
        for key, attribute_report in class_report_dict.items():
            class_report[key] = _AttrReport(key, **attribute_report)
        self.reports[_type] = _TypeReport(class_report, _type)

    def clear(self):
        self.reports = {}
