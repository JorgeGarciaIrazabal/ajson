import unittest

from ajson.class_decorator import AJson
from ajson.json_class_reports import JsonClassReports, ISO_FORMAT, AJsonUniqueClassNameError


class TestAJsonDecorator(unittest.TestCase):
    def setUp(self):
        JsonClassReports().clear()

    def test_annotation_class_creates_report_with_group(self):
        @AJson()
        class AJDA:
            def __init__(self):
                self.a = 10  # testing @aj{ "groups": ["admin"]}

        reports = JsonClassReports().reports
        self.assertIn(AJDA, reports)
        self.assertEqual(len(reports.keys()), 1)
        self.assertEqual(reports[AJDA].get("a").groups, {"admin"})
        self.assertEqual(reports[AJDA].get("a").datetime_format, ISO_FORMAT)
        self.assertEqual(reports[AJDA].get("a").name, "a")

    def test_annotation_class_creates_report_with_group_and_name(self):
        @AJson()
        class AJDB:
            def __init__(self):
                self.a = 10  # testing @aj{ "groups": ["admin"], "name": "annotation"}

        reports = JsonClassReports().reports
        self.assertIn(AJDB, reports)
        self.assertEqual(reports[AJDB].get("a").datetime_format, ISO_FORMAT)
        self.assertEqual(reports[AJDB].get("a").name, "annotation")

    def test_annotation_class_creates_report_all_parameters(self):
        @AJson()
        class AJDC:
            def __init__(self):
                self.a = 10
                '''
                    @aj{ 
                    "groups": [
                        "admin",
                        "public"
                        ],
                    "name": "annotation",
                    "d_format": "Y-M-D"
                    }
                '''

        reports = JsonClassReports().reports
        self.assertIn(AJDC, reports)
        self.assertEqual(reports[AJDC].get("a").groups, {"admin", "public"})
        self.assertEqual(reports[AJDC].get("a").datetime_format, "Y-M-D")
        self.assertEqual(reports[AJDC].get("a").name, "annotation")

    def test_annotation_class_name_has_to_be_unique(self):
        @AJson(class_name="AJDD")
        class AJDD:
            pass

        with self.assertRaises(AJsonUniqueClassNameError):
            @AJson(class_name="AJDD")
            class AJDE:
                pass



