from ajson.json_type_reports import JsonTypeReports
from ajson.type_inspector import TypeInspector


def AJson():
    def wrapper(cls: type):
        report = TypeInspector().inspect_type(cls)
        JsonTypeReports().add(cls, report)
        return cls

    return wrapper