import unittest

from ajson.class_decorator import AJson
from ajson.json_type_reports import JsonTypeReports, ISO_FORMAT


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

    def test_class_with_parent_get_parent_properties(self):
        @AJson()
        class AIPP1:
            a: int = 10  # @aj(name=aa)
            b: int = 20  # @aj(name=bb)

        @AJson()
        class AIPP2(AIPP1):
            c: int = 30  # @aj(name=cc)
            d: int = 40  # @aj(name=dd)

        reports = JsonTypeReports().reports
        self.assertIn(AIPP1, reports)
        self.assertIn(AIPP2, reports)
        self.assertEqual(reports[AIPP1].get("a").name, 'aa')
        self.assertEqual(reports[AIPP1].get("b").name, 'bb')
        self.assertEqual(reports[AIPP2].get("a").name, 'aa')
        self.assertEqual(reports[AIPP2].get("b").name, 'bb')
        self.assertEqual(reports[AIPP2].get("c").name, 'cc')
        self.assertEqual(reports[AIPP2].get("d").name, 'dd')

    def test_class_with_parent_overwrites_parent_properties(self):
        @AJson()
        class AIWP1:
            a: int = 10  # @aj(name=aa)

        @AJson()
        class AIWP2(AIWP1):
            a: int = 30  # @aj(name=aaa)
            d: int = 40  # @aj(name=dd)

        reports = JsonTypeReports().reports
        self.assertIn(AIWP1, reports)
        self.assertIn(AIWP2, reports)
        self.assertEqual(reports[AIWP1].get("a").name, 'aa')
        self.assertEqual(reports[AIWP2].get("a").name, 'aaa')
        self.assertEqual(reports[AIWP2].get("d").name, 'dd')
