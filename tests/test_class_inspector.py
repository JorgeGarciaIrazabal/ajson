import inspect
import unittest

from _class_inspector import ClassInspector


class TestClassInspector(unittest.TestCase):
    def test_simple_class_with_inline_annotation_gets_the_as_params_and_identifies_the_attributes(self):
        class CIA:
            def __init__(self):
                self.a = 10  # testing @as{ "groups": 1}
                self.b = 10  # testing @ac{ "groups": ["test"]}

        report = ClassInspector().inspect_class(CIA)
        self.assertEqual(len(report.keys()), 1)
        self.assertDictEqual(report, {
            "a": {"groups": 1}
        })

    def test_parse_report_with_as_in_multiline(self):
        class CIB:
            def __init__(self):
                self.a = 10
                '''
                    @as{
                        "groups": [
                            1,
                            2,
                            3
                        ]
                    }
                '''

        report = ClassInspector().inspect_class(CIB)
        self.assertEqual(len(report.keys()), 1)
        self.assertDictEqual(report, {
            "a": {"groups": [1, 2, 3]}
        })
