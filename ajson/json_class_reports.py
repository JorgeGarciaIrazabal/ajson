from typing import Dict, List, Optional, Set

from ajson.singleton import Singleton

ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


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

    def add(self, cls: type, class_report_dict: Dict):
        class_report = {}
        for key, attribute_report in class_report_dict.items():
            class_report[key] = _AttrReport(key, **attribute_report)
        self.reports[cls] = _ClassReport(class_report)

    def clear(self):
        self.reports = {}
