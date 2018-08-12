from typing import Dict, List, Optional, Set

from singleton import Singleton


class _AttrReport(object):
    def __init__(self, attribute_name: str = 3, **kwargs):
        self.groups: Optional[Set[str]]
        self.name: str
        self.datetime_format: str
        self.float_format: str
        self.attribute_name: str

        self.attribute_name: attribute_name
        self.groups = kwargs.get('groups', None)
        self.groups = self.groups if self.groups is None else set(self.groups)
        self.name = kwargs.get('name', attribute_name)
        self.datetime_format = kwargs.get('d_format', None)
        self.float_format = kwargs.get('f_format', None)


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


class JsonClassReports(object, metaclass=Singleton):
    def __init__(self):
        self.reports: Dict[type, _ClassReport] = {}

    def add(self, cls: type, class_report_dict: Dict):
        class_report = {}
        for key, attribute_report in class_report_dict.items():
            class_report[key] = _AttrReport(key, **attribute_report)
        self.reports[cls] = _ClassReport(class_report)

    def clear(self):
        self.reports = {}
