import unittest

from _class_decorator import AJson
from _json_class_reports import JsonClassReports


class TestAJsonDecorator(unittest.TestCase):
    def setUp(self):
        JsonClassReports().clear()

    def test_annotation_class_creates_report_with_group(self):
        @AJson
        class AJDA:
            def __init__(self):
                self.a = 10  # testing @as{ "groups": ["admin"]}

        reports = JsonClassReports().reports
        self.assertIn(AJDA, reports)
        self.assertEqual(len(reports.keys()), 1)
        self.assertEqual(reports[AJDA]["a"].groups, ["admin"])
        self.assertIsNone(reports[AJDA]["a"].float_format)
        self.assertIsNone(reports[AJDA]["a"].datetime_format)
        self.assertEqual(reports[AJDA]["a"].name, "a")

    def test_annotation_class_creates_report_with_group_and_name(self):
        @AJson
        class AJDB:
            def __init__(self):
                self.a = 10  # testing @as{ "groups": ["admin"], "name": "annotation"}

        reports = JsonClassReports().reports
        self.assertIn(AJDB, reports)
        self.assertIsNone(reports[AJDB]["a"].float_format)
        self.assertIsNone(reports[AJDB]["a"].datetime_format)
        self.assertEqual(reports[AJDB]["a"].name, "annotation")

    def test_annotation_class_creates_report_all_parameters(self):
        @AJson
        class AJDC:
            def __init__(self):
                self.a = 10
                '''
                    @as{ 
                    "groups": [
                        "admin",
                        "public"
                        ],
                    "name": "annotation",
                    "d_format": "Y-M-D",
                    "f_format": ".2f"
                    }
                '''

        reports = JsonClassReports().reports
        self.assertIn(AJDC, reports)
        self.assertEqual(reports[AJDC]["a"].groups, ["admin", "public"])
        self.assertEqual(reports[AJDC]["a"].datetime_format, "Y-M-D")
        self.assertEqual(reports[AJDC]["a"].float_format, ".2f")
        self.assertEqual(reports[AJDC]["a"].name, "annotation")
