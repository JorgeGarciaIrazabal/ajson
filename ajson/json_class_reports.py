from typing import Dict, List, Optional, Set

from ajson.singleton import Singleton

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


class AJsonUniqueClassNameError(Exception):
    def __init__(self, class_name: str):
        self.class_name = class_name

    def __str__(self, *args, **kwargs):
        return "{0} Already used in another class. AJson classes have to be unique, " \
               "Set a different name in the @AJson decorator," \
               " for example @AJson(class_name='{0}_New')".format(self.class_name)


class _AttrReport(object):
    def __init__(self, attribute_name: str = 3, **kwargs):
        self.groups: Optional[Set[str]] = kwargs.get("groups", None)
        self.name: str = kwargs.get("name", attribute_name)
        self.datetime_format: str = kwargs.get("d_format", ISO_FORMAT)  # iso format
        self.attribute_name: str = attribute_name

        self.groups = self.groups if self.groups is None else set(self.groups)


class _ClassReport(object):
    def __init__(self, attr_reports: Dict[str, _AttrReport]):
        self.report_map: Dict[str, _AttrReport] = attr_reports

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


class JsonClassReports(object, metaclass=Singleton):
    def __init__(self):
        self.reports: Dict[type, _ClassReport] = {}
        self.name_to_csl_map: Dict[str, type] = {}

    def add(self, cls: type, cls_name: str, class_report_dict: Dict):
        class_report = {}
        for key, attribute_report in class_report_dict.items():
            class_report[key] = _AttrReport(key, **attribute_report)
        self.reports[cls] = _ClassReport(class_report)
        if cls_name in self.name_to_csl_map:
            raise AJsonUniqueClassNameError(cls_name)
        self.name_to_csl_map[cls_name] = cls

    def clear(self):
        self.reports = {}
