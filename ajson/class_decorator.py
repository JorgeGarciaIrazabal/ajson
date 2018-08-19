from builtins import str
from typing import Optional

from ajson.class_inspector import ClassInspector
from ajson.json_class_reports import JsonClassReports


def AJson(class_name: Optional[str] = None):
    def wrapper(cls: type):
        report = ClassInspector().inspect_class(cls)
        final_class_name = cls.__name__ if class_name is None else class_name
        JsonClassReports().add(cls, final_class_name, report)
        return cls

    return wrapper