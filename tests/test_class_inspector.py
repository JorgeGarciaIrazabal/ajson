import json
import unittest

from ajson.type_inspector import TypeInspector


class TestClassInspector(unittest.TestCase):
    def test_simple_class_with_inline_annotation_gets_the_as_params_and_identifies_the_attributes(self):
        class CIA:
            def __init__(self):
                self.a = 10  # testing @aj(groups=["test"] required)
                self.b = 10  # @ac( "groups": ["test"])

        report = TypeInspector().inspect_type(CIA)
        self.assertEqual(len(report.keys()), 1)
        self.assertDictEqual(report, {
            'a': {'groups': '["test"]', 'required': ''}
        })

    def test_parse_report_with_as_in_multiline(self):
        class CIB:
            def __init__(self):
                self.a = 10
                '''
                    @aj(
                        groups="[
                            1,
                            2,
                            3
                        ]"
                    )
                '''

        report = TypeInspector().inspect_type(CIB)
        self.assertEqual(len(report.keys()), 1)
        self.assertEqual(json.loads(report['a']['groups']), [1, 2, 3])

    def test_annotation_without_attribute_is_ignore(self):
        class CID:
            def __init__(self):
                '''
                    @aj(
                        "groups":  1
                    )
                '''
                self.b = 6  # @aj(name=test)

        report = TypeInspector().inspect_type(CID)
        self.assertEqual(len(report.keys()), 1)
        self.assertDictEqual(report, {
            'b': {'name': 'test'}
        })

    def test_annotation_gets_properties_too(self):
        class CIEP:
            def __init__(self):
                self._a = 10

            @property
            def a(self):
                """ @aj(name=new_a) """
                return self._a + 10

        report = TypeInspector().inspect_type(CIEP)
        self.assertEqual(len(report.keys()), 1)
        self.assertDictEqual(report, {
            'a': {'name': 'new_a'}
        })
