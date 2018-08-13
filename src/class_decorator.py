from src.class_inspector import ClassInspector
from src.json_class_reports import JsonClassReports


def AJson(cls: type):
    report = ClassInspector().inspect_class(cls)
    JsonClassReports().add(cls, report)
    return cls
