from builtins import str
from typing import Optional

from ajson.class_inspector import ClassInspector
from ajson.json_class_reports import JsonTypeReports


def AJson():
    def wrapper(cls: type):
        report = ClassInspector().inspect_class(cls)
        JsonTypeReports().add(cls, report)
        return cls

    return wrapper