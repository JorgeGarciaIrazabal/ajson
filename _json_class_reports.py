from typing import Dict, List, Optional

from singleton import Singleton


class _AttrReport(object):
    def __init__(self, attribute_name: str = 3, **kwargs):
        self.groups: Optional[List[str]]
        self.name: str
        self.datetime_format: str
        self.float_format: str
        self.attribute_name: str

        self.attribute_name: attribute_name
        self.groups = kwargs.get('groups', None)
        self.name = kwargs.get('name', attribute_name)
        self.datetime_format = kwargs.get('d_format', None)
        self.float_format = kwargs.get('f_format', None)


class JsonClassReports(object, metaclass=Singleton):
    def __init__(self):
        self.reports: Dict[type, Dict[str, _AttrReport]] = {}

    def add(self, cls: type, class_report_dict: Dict):
        class_report = {}
        for key, attribute_report in class_report_dict.items():
            class_report[key] = _AttrReport(key, **attribute_report)
        self.reports[cls] = class_report

    def clear(self):
        self.reports = {}
