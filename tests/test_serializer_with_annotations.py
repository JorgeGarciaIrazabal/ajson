import json
import unittest

from ajson.aserializer import ASerializer
from ajson.json_type_reports import AJsonEmptyRequiredAttributeError, AJsonValidationError
from tests.types_for_tests.test_serializaer_with_annotations_types import *


class TestSerializationWithAnnotations(unittest.TestCase):
    # Test with AJson decoration
    def setUp(self):
        self.serializer = ASerializer()

    def test_empty_object_with_ajson_serialize_obj_if_no_groups_passed(self):
        serialization = self.serializer.serialize(SEmptyObjectAJson())
        self.assertEqual(len(json.loads(serialization).keys()), 1)
        self.assertEqual(json.loads(serialization)['a'], 1)

        serialization = self.serializer.serialize(SEmptyObjectAJson(), groups=[])
        self.assertEqual(len(json.loads(serialization).keys()), 0)

    def test_object_with_empty_aj_annotation_is_serialized_too_if_no_group_is_passed(self):
        serialization = self.serializer.serialize(SSimpleObjectAJson())
        self.assertEqual(len(json.loads(serialization).keys()), 2)
        self.assertEqual(json.loads(serialization)['a'], 1)
        self.assertEqual(json.loads(serialization)['b'], 1)

        serialization = self.serializer.serialize(SSimpleObjectAJson(), groups=[])
        self.assertEqual(len(json.loads(serialization).keys()), 0)

    def test_object_with_ajson_returns_only_attributes_in_group(self):
        serialization = self.serializer.serialize(SSimpleObjectAJsonWithGroups(), groups=['admin'])
        self.assertEqual(len(json.loads(serialization).keys()), 1)
        self.assertEqual(json.loads(serialization)['a'], 1)

        serialization = self.serializer.serialize(SSimpleObjectAJsonWithGroups(), groups=['public'])
        self.assertEqual(len(json.loads(serialization).keys()), 1)
        self.assertEqual(json.loads(serialization)['b'], 2)

    def test_object_with_ajson_returns_only_attributes_in_group_with_nested_references(self):
        dict_obj = self.serializer.to_dict(SSimpleObjectAJsonNested2(), groups=['admin'])
        self.assertEqual(len(dict_obj.keys()), 1)
        self.assertEqual(dict_obj['nested1'], {'a': 1})

        dict_obj = self.serializer.to_dict(SSimpleObjectAJsonNested2(), groups=['admin', 'public'])
        self.assertEqual(len(dict_obj.keys()), 2)
        self.assertEqual(dict_obj['nested1'], {'a': 1, 'b': 2})
        self.assertEqual(dict_obj['nested2'], {'a': 1, 'b': 2})

    def test_object_with_ajson_and_date_format_returns_the_right_date_format(self):
        dict_obj = self.serializer.to_dict(SSimpleObjectWithDate())
        self.assertEqual(len(dict_obj.keys()), 2)
        self.assertEqual(dict_obj['time1'], '2000/02/01')
        self.assertEqual(dict_obj['time2'], '2010--0240')

    def test_list_ob_objects_is_serialized_with_the_right_groups(self):
        list_obj = self.serializer.to_dict([SSimpleObjectAJsonWithGroups()], groups=['admin'])
        self.assertEqual(len(list_obj), 1)
        self.assertEqual(list_obj[0]['a'], 1)

    def test_serialize_only_attrs_with_the_right_groups(self):
        obj_dict = self.serializer.to_dict(SObjectWithGroupsAndNoGroups(), groups=['admin'])
        self.assertEqual(len(obj_dict.keys()), 1)
        self.assertEqual(obj_dict['a'], 1)

        obj_dict = self.serializer.to_dict(SObjectWithGroupsAndNoGroups(), groups=['public'])
        self.assertEqual(len(obj_dict.keys()), 1)
        self.assertEqual(obj_dict['b'], 2)

        obj_dict = self.serializer.to_dict(SObjectWithGroupsAndNoGroups())
        self.assertEqual(len(obj_dict.keys()), 4)

    def test_serialize_properties_too(self):
        obj_dict = self.serializer.to_dict(SObjectWithProperties())
        self.assertEqual(len(obj_dict.keys()), 2)
        self.assertEqual(obj_dict['a'], 1)
        self.assertEqual(obj_dict['b'], 2)

        obj_dict = self.serializer.to_dict(SObjectWithProperties(), groups=['g1'])
        self.assertEqual(len(obj_dict.keys()), 1)
        self.assertEqual(obj_dict['b'], 2)

    # Unserialize
    def test_simple_entity_is_unserialize_from_dict(self):
        dict_obj = {
            'a': 10
        }

        obj: USSimpleObjectAJson = self.serializer.from_dict(dict_obj, USSimpleObjectAJson)
        self.assertEqual(obj.a, 10)

    def test_unserialize_with_different_name_nade_date_time_format(self):
        dict_obj = {
            'a': 10,  # this should be ignored
            'my_mane': 20,
            'date': '2010--0240',
        }

        obj: USNameAndDateObjectAJson = self.serializer.from_dict(dict_obj, USNameAndDateObjectAJson)
        self.assertEqual(obj.a, 20)
        self.assertIsInstance(obj.date, datetime)

    def test_unserialize_list_returns_list_of_objects(self):
        list_dict = [
            {
                'my_mane': 1,
                'date': '2000/01/01',
            },
            {
                'my_mane': 2,
                'date': '2000/02/01',
            },
            {
                'my_mane': 3,
                'date': '2000/03/01',
            },
        ]

        list_obj: List[USNameAndDateObjectAJson2] = self.serializer.from_dict(list_dict, USNameAndDateObjectAJson2)
        self.assertEqual(len(list_obj), 3)
        self.assertEqual(list_obj[0].a, 1)
        self.assertEqual(list_obj[0].date.month, 1)
        self.assertEqual(list_obj[1].date.month, 2)
        self.assertEqual(list_obj[2].date.month, 3)

    def test_unserialize_nested_objects(self):
        obj_dict = {
            'nested': {
                'my_mane': 3,
                'date': '2003/01/01',
            },
        }

        obj: USNestedObject1 = self.serializer.from_dict(obj_dict, USNestedObject1)
        self.assertEqual(obj.nested.a, 3)
        self.assertIsInstance(obj.nested.date, datetime)
        self.assertEqual(obj.nested.date.year, 2003)

    def test_unserialize_nested_with_object_lists(self):
        obj_dict = {
            'nested_list': [
                {
                    'my_mane': 3,
                    'date': '2003/01/01',
                }
            ],
        }

        obj: USNestedListObject = self.serializer.from_dict(obj_dict, USNestedListObject)
        self.assertEqual(obj.nested_list[0].a, 3)
        self.assertIsInstance(obj.nested_list[0].date, datetime)
        self.assertEqual(obj.nested_list[0].date.year, 2003)

    def test_unserialize_with_required_throws_if_required_is_not_provided(self):
        dict_obj = {
            'b': 1,
        }
        with self.assertRaises(AJsonEmptyRequiredAttributeError):
            self.serializer.from_dict(dict_obj, USRequiredObject)

    def test_unserialize_with_required_throws_if_required_is_null(self):
        str_obj = '{"b": 1, "a": null }'
        with self.assertRaises(AJsonEmptyRequiredAttributeError):
            self.serializer.unserialize(str_obj, USRequiredObject)

    def test_unserialize_object_without_annotations_should_be_generated_with_default_behaviour(self):
        dict_obj = {
            'b': 1,
            'a': 10,
        }
        obj: USWithoutAnnotationsObject = self.serializer.from_dict(dict_obj, USWithoutAnnotationsObject)
        self.assertEqual(obj.a, 10)
        self.assertEqual(obj.b, 1)

    def test_unserialize_raises_error_if_type_do_not_match(self):
        dict_obj = {
            'b': None,
            'a': 10,
        }
        obj: USWithHintsObject = self.serializer.from_dict(dict_obj, USWithHintsObject)

        self.assertIsNone(obj.b)
        self.assertEqual(obj.a, 10)

    def test_unserialize_allows_validation_with_multi_type(self):
        obj: USWithMultiTypeHintsObject = self.serializer.from_dict({'a': 10}, USWithMultiTypeHintsObject)
        self.assertEqual(obj.a, 10)
        obj: USWithMultiTypeHintsObject = self.serializer.from_dict({'a': 'str'}, USWithMultiTypeHintsObject)
        self.assertEqual(obj.a, 'str')
        with self.assertRaises(AJsonValidationError):
            self.serializer.from_dict({'a': 10.13}, USWithMultiTypeHintsObject)

    def test_unserialize_properties(self):
        obj: USWithProperties = self.serializer.from_dict({'a': 10, 'b': 5}, USWithProperties)
        self.assertEqual(obj.a, 10)
        self.assertEqual(obj.b, 2)  # not updated as it is not using the name
        obj: USWithProperties = self.serializer.from_dict({'a': 4, 'new_b': 20}, USWithProperties)
        self.assertEqual(obj.a, 4)
        self.assertEqual(obj.b, 20)
