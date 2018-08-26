import unittest

from ajson.class_decorator import AJson
from ajson.json_class_reports import JsonTypeReports, ISO_FORMAT


class TestAJsonDecorator(unittest.TestCase):
    def setUp(self):
        self.old_reports = JsonTypeReports().reports
        JsonTypeReports().clear()

    def tearDown(self):
        JsonTypeReports().reports = self.old_reports

    def test_annotation_class_creates_report_with_group(self):
        @AJson()
        class AJDA:
            def __init__(self):
                self.a = 10  # testing @aj(groups=["admin"])

        reports = JsonTypeReports().reports
        self.assertIn(AJDA, reports)
        self.assertEqual(len(reports.keys()), 1)
        self.assertEqual(reports[AJDA].get("a").groups, {"admin"})
        self.assertEqual(reports[AJDA].get("a").datetime_format, ISO_FORMAT)
        self.assertEqual(reports[AJDA].get("a").name, "a")

    def test_annotation_class_creates_report_with_group_and_name(self):
        @AJson()
        class AJDB:
            def __init__(self):
                self.a = 10  # testing @aj(groups=["admin"] name=annotation)

        reports = JsonTypeReports().reports
        self.assertIn(AJDB, reports)
        self.assertEqual(reports[AJDB].get("a").datetime_format, ISO_FORMAT)
        self.assertEqual(reports[AJDB].get("a").name, "annotation")

    def test_annotation_class_creates_report_all_parameters(self):
        @AJson()
        class AJDC:
            def __init__(self):
                self.a = 10
                '''
                    @aj( 
                    groups="[
                        'admin',
                        'public'
                        ]"
                    name=annotation
                    d_format=Y-M-D
                    )
                '''

        reports = JsonTypeReports().reports
        self.assertIn(AJDC, reports)
        self.assertEqual(reports[AJDC].get("a").groups, {"admin", "public"})
        self.assertEqual(reports[AJDC].get("a").datetime_format, "Y-M-D")
        self.assertEqual(reports[AJDC].get("a").name, "annotation")



