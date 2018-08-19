from builtins import str
from typing import Optional

from ajson.class_inspector import ClassInspector
from ajson.json_class_reports import JsonClassReports


def AJson(type_name: Optional[str] = None):
    def wrapper(cls: type):
        report = ClassInspector().inspect_class(cls)
        final_class_name = cls.__name__ if type_name is None else type_name
        JsonClassReports().add(cls, final_class_name, report)
        return cls

    return wrapper